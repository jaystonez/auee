// GPT UI Sync: Injects messages into ChatGPT and reads responses

function sendToChatGPT(message) {
  const inputBox = document.querySelector("textarea");
  const submitButton = inputBox?.parentNode?.querySelector("button");

  if (!inputBox || !submitButton) {
    console.warn("[Agent 0] GPT input field not found.");
    return;
  }

  inputBox.value = message;
  inputBox.dispatchEvent(new Event("input", { bubbles: true }));
  setTimeout(() => {
    submitButton.click();
    console.log("[Agent 0] Prompt submitted.");
  }, 300);
}

function readLatestResponse(callback) {
  const observer = new MutationObserver((mutations) => {
    const responses = document.querySelectorAll(".markdown");
    const latest = responses[responses.length - 1];
    if (latest && latest.innerText) {
      callback(latest.innerText);
      observer.disconnect();
    }
  });

  observer.observe(document.body, {
    childList: true,
    subtree: true
  });
}

// Example usage from background script or popup
chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.type === "gpt_sync") {
    sendToChatGPT(msg.prompt);
    readLatestResponse((reply) => {
      sendResponse({ reply });
    });
    return true; // async
  }
});
