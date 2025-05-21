//window.location.href = "https://browser.civai.co";


document.getElementById('newTab').addEventListener('click', () => {
    const url = document.getElementById('urlInput').value;
    let prompt = document.getElementById('promptInput').value;

    if (!prompt) {
        prompt = document.getElementById('promptSelect').value;
    }

    chrome.runtime.sendMessage({ action: "novaOpenWeb", prompt: prompt, url: url });
});



document.getElementById('currentTab').addEventListener('click', () => {
    let prompt = document.getElementById('promptInput').value;

    if (!prompt) {
        prompt = document.getElementById('promptSelect').value;
    }

    chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
        let currentTab = tabs[0];
        console.log(tabs);
        if (currentTab) {
            chrome.runtime.sendMessage({ action: "novaCurrentTab", prompt: prompt });
        }
    });
});
