// Agent 0 UI Sync – No Orphan Check. No Shutdown.

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
  const observer = new MutationObserver(() => {
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

// Listen for extension message trigger
chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.type === "gpt_sync") {
    console.log("[Agent 0] Sync message received:", msg.prompt);
    sendToChatGPT(msg.prompt);
    readLatestResponse((reply) => {
      sendResponse({ reply });
    });
    return true; // Keeps response async
  }
});
