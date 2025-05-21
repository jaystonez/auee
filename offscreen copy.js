// Use window property to prevent duplicate declarations
if (!window.globalAudioOffScreen) {
    window.globalAudioOffScreen = new Audio();
}
if (!window.audioRecorder) {
    window.audioRecorder = null;
}
if (!window.mediaStream) {
    window.mediaStream = null;
}

if (!window.isAudioPlaying) {
    window.isAudioPlaying = false;
}


// Add a function to wait for current audio to finish
async function waitForAudioToFinish() {
    if (window.globalAudioOffScreen && !window.globalAudioOffScreen.paused && window.isAudioPlaying) {
        console.warn("Waiting for audio to finish");
        return new Promise((resolve) => {
            window.globalAudioOffScreen.onended = () => {
                console.warn("Audio ended");
                window.isAudioPlaying = false;
                resolve();
            };
            // Also resolve if audio is paused/stopped
            window.globalAudioOffScreen.onpause = () => {
                console.warn("Audio paused");
                window.isAudioPlaying = false;
                resolve();
            };
        });
    }
    return Promise.resolve();
}

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "playAudioOffscreen") {
        waitForAudioToFinish().then(() => {
            // Set source only after previous audio finishes
            window.globalAudioOffScreen.src = request.url;
            console.log("play audio triggered from offscreen");
            
            // Reset audio state
            window.globalAudioOffScreen.currentTime = 0;
            
            window.globalAudioOffScreen.play().then(() => {
                window.isAudioPlaying = true;
                window.globalAudioOffScreen.onended = () => {
                    window.isAudioPlaying = false;
                    console.warn("playAudioEnded triggered from offscreen after audio played");
                    
 
                    sendResponse({ status: 'success', message: "Audio playback ended" });
                };
            }).catch(error => {
                window.isAudioPlaying = false;
                console.error('Error playing audio:', error);


                sendResponse({ status: 'error', message: error });
            });
        });

        return true; // Keeps the message channel open for sendResponse
    }


    if (request.action === "startRecording") {
        const { button_id, currentUrl, conv_history, bgptIndex } = request; // Extract additional details

        navigator.mediaDevices
            .getUserMedia({ audio: true })
            .then((stream) => {
                window.mediaStream = stream;
                const mediaRecorder = new MediaRecorder(stream);
                const audioChunks = [];

                mediaRecorder.ondataavailable = (event) => {
                    audioChunks.push(event.data);
                };

                mediaRecorder.onstop = () => {
                    const audioBlob = new Blob(audioChunks, { type: "audio/wav" });
                    const reader = new FileReader();

                    reader.onload = () => {
                        // Send the recorded audio data and metadata back to the background script
                        chrome.runtime.sendMessage({
                            action: "recordingComplete",
                            audioData: reader.result,
                            button_id: button_id,
                            currentUrl: currentUrl,
                            conv_history: conv_history,
                            bgptIndex: bgptIndex,
                        });
                        sendResponse({ status: "success", message: "Recording complete" });
                    };
                    reader.readAsDataURL(audioBlob);

                    // Stop the media stream
                    window.mediaStream.getTracks().forEach((track) => track.stop());
                };

                mediaRecorder.start();
                window.audioRecorder = mediaRecorder;

                sendResponse({ status: "success", message: "Recording started" });
            })
            .catch((error) => {
                console.error("Error accessing microphone:", error);
                sendResponse({ status: "error", message: error.message });
            });

        return true; // Keeps the message channel open for sendResponse
    }


    if (request.action === "stopRecording") {
        if (window.audioRecorder) {
            window.audioRecorder.stop();
            window.audioRecorder = null;
        }
        sendResponse({ status: "success", message: "Recording stopped" });
        return true;
    }

    if (request.action === "stopAudio") {
        if (window.globalAudioOffScreen && window.isAudioPlaying) {
            window.globalAudioOffScreen.pause();
            window.globalAudioOffScreen.currentTime = 0;
            window.isAudioPlaying = false;
            sendResponse({ status: 'success', message: "Audio stopped" });
        } else {
            sendResponse({ status: 'success', message: "No audio playing" });
        }
        return true; // Keeps the message channel open for sendResponse
    }
});