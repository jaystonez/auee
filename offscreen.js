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

// Store chunks until complete
if (!window.audioChunks) {
    window.audioChunks = [];
}

// Add MediaSource support
if (!window.mediaSource) {
    window.mediaSource = null;
}
if (!window.sourceBuffer) {
    window.sourceBuffer = null;
}

// Add queue for chunks
if (!window.chunkQueue) {
    window.chunkQueue = [];
}

// Add a function to wait for current audio to finish
async function waitForAudioToFinish() {
    if (window.globalAudioOffScreen && !window.globalAudioOffScreen.paused && window.isAudioPlaying) {
        console.warn("Waiting for audio to finish");
        return new Promise((resolve) => {
            const checkAudio = () => {
                if (!window.isAudioPlaying) {
                    console.warn("Audio finished, continuing");

                    window.globalAudioOffScreen.pause();
                    window.globalAudioOffScreen.currentTime = 0;
                    window.isAudioPlaying = false;
                    
                    // Clean up MediaSource
                    if (window.mediaSource) {
                        if (window.sourceBuffer) {
                            try {
                                window.sourceBuffer.abort();
                            } catch (e) {
                                console.warn("Error aborting source buffer:", e);
                            }
                        }
                        try {
                            window.mediaSource.endOfStream();
                        } catch (e) {
                            console.warn("Error ending media stream:", e);
                        }
                    }
                    resolve();
                } else {
                    setTimeout(checkAudio, 100);
                }
            };
            window.globalAudioOffScreen.onended = () => {
                console.warn("Audio ended");
                window.isAudioPlaying = false;
                resolve();
            };
            window.globalAudioOffScreen.onpause = () => {
                console.warn("Audio paused");
                window.isAudioPlaying = false;
                resolve();
            };
            checkAudio();
        });
    }
    return Promise.resolve();
}

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "playAudioOffscreen") {

        console.warn("playAudioOffscreen called");
        
        // Only wait for previous audio to finish when starting a new stream
        const shouldWait = !window.mediaSource && request.blobData || request.url;
        
        (shouldWait ? waitForAudioToFinish() : Promise.resolve()).then(() => {
            if (request.blobData) {
                if (!window.mediaSource) {
                    // First chunk - initialize MediaSource
                    window.mediaSource = new MediaSource();
                    window.globalAudioOffScreen.src = URL.createObjectURL(window.mediaSource);
                    
                    window.mediaSource.addEventListener('sourceopen', () => {
                        console.log("MediaSource opened");
                        try {
                            window.sourceBuffer = window.mediaSource.addSourceBuffer('audio/mpeg');
                            
                            // Process first chunk
                            const chunk = new Uint8Array(request.blobData);
                            console.log("Processing first chunk, length:", chunk.length);
                            window.sourceBuffer.appendBuffer(chunk);

                            // Handle subsequent chunks
                            window.sourceBuffer.addEventListener('updateend', () => {
                                console.log("Buffer updated, queue length:", window.chunkQueue.length);
                                
                                // Start playback after first chunk is processed
                                if (!window.isAudioPlaying) {
                                    window.globalAudioOffScreen.play().then(() => {
                                        window.isAudioPlaying = true;
                                        console.log("Playback started");
                                    }).catch(err => console.error("Playback failed:", err));
                                }

                                // Process next chunk if available
                                if (window.chunkQueue.length > 0 && !window.sourceBuffer.updating) {
                                    const nextChunk = window.chunkQueue.shift();
                                    try {
                                        window.sourceBuffer.appendBuffer(nextChunk);
                                    } catch (e) {
                                        console.error("Error appending next chunk:", e);
                                    }
                                }
                            });

                        } catch (e) {
                            console.error("Error setting up MediaSource:", e);
                        }
                    });
                } else {
                    // Subsequent chunks
                    const chunk = new Uint8Array(request.blobData);
                    console.log("Received chunk, length:", chunk.length);
                    
                    if (!window.sourceBuffer.updating) {
                        try {
                            window.sourceBuffer.appendBuffer(chunk);
                        } catch (e) {
                            console.error("Error appending chunk:", e);
                            window.chunkQueue.push(chunk);
                        }
                    } else {
                        window.chunkQueue.push(chunk);
                    }
                }
            } else if (request.done) {
                // End of stream
                console.log("Stream ended, remaining chunks:", window.chunkQueue.length);
                if (window.sourceBuffer && !window.sourceBuffer.updating) {
                    try {
                        window.mediaSource.endOfStream();
                    } catch (e) {
                        console.error("Error ending stream:", e);
                    }
                }
                // Reset state after stream ends
                window.mediaSource = null;
                window.sourceBuffer = null;
                window.chunkQueue = [];
                window.isAudioPlaying = false;
                window.globalAudioOffScreen.onended = null;  // Clear event handler
            } else if (request.url) {
                // Regular audio URL playback
                window.globalAudioOffScreen.src = request.url;
                console.log("play audio triggered from offscreen");
                window.globalAudioOffScreen.currentTime = 0;
                window.globalAudioOffScreen.play().then(() => {
                    window.isAudioPlaying = true;
                });
            }

            // Common event handlers
            window.globalAudioOffScreen.onended = () => {
                window.isAudioPlaying = false;
                console.warn("playAudioEnded triggered from offscreen after audio played");
                // Reset state when audio ends
                window.mediaSource = null;
                window.sourceBuffer = null;
                window.chunkQueue = [];
                sendResponse({ status: 'success', message: "Audio playback ended" });
            };
        }).catch(error => {
            window.isAudioPlaying = false;
            console.error('Error playing audio:', error);
            // Reset state on error
            window.mediaSource = null;
            window.sourceBuffer = null;
            window.chunkQueue = [];
            sendResponse({ status: 'error', message: error });
        });

        return true;
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

        console.warn("stopAudio called in offscreen");
        
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
