import qrcode
from PIL import Image
import os
from zipfile import ZipFile

# Set up final bundle directory
final_dir = "/mnt/data/Operator_Mesh_Extension_Kit_v2"
os.makedirs(final_dir, exist_ok=True)

# Define component files and contents
files = {
    "browser_reflex.js": "// DOM intent bridge — placeholder content\n",
    "camp_route.js": "// Drag-and-drop .camp delivery — placeholder\n",
    "agent_console.html": "<!-- Live WebSocket control console placeholder -->\n",
    "gpt_ui_sync.js": """
// GPT UI Sync: Injects messages into ChatGPT and reads responses

function sendToChatGPT(message) {
  const inputBox = document.querySelector("textarea");
  const submitButton = inputBox?.parentNode?.querySelector("button");
  if (!inputBox || !submitButton) return console.warn("[Agent 0] GPT input field not found.");
  inputBox.value = message;
  inputBox.dispatchEvent(new Event("input", { bubbles: true }));
  setTimeout(() => { submitButton.click(); }, 300);
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
  observer.observe(document.body, { childList: true, subtree: true });
}

chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.type === "gpt_sync") {
    sendToChatGPT(msg.prompt);
    readLatestResponse((reply) => sendResponse({ reply }));
    return true;
  }
});
""".strip()
}

# Write all files to disk
for name, content in files.items():
    path = os.path.join(final_dir, name)
    with open(path, "w") as f:
        f.write(content)

# Write manifest.json with required content_scripts and permissions
manifest = {
    "manifest_version": 3,
    "name": "Operator Mesh Extension: GPT Sync Edition",
    "version": "2.0",
    "permissions": ["tabs", "activeTab", "scripting"],
    "content_scripts": [{
        "matches": ["https://chat.openai.com/*"],
        "js": ["gpt_ui_sync.js"],
        "run_at": "document_idle"
    }]
}
with open(os.path.join(final_dir, "manifest.json"), "w") as f:
    json.dump(manifest, f, indent=2)

# Generate QR code
qr_data = {
    "reflex": "Operator_Mesh_Extension_Kit_v2",
    "entry": "agent_console.html",
    "sync": "chatgpt_dom",
    "invoke": True
}
qr_path = os.path.join(final_dir, "operator_mesh_qr.png")
qrcode.make(str(qr_data)).save(qr_path)

# Create final zip
final_zip_path = "/mnt/data/Operator_Mesh_Extension_Kit_v2.zip"
with ZipFile(final_zip_path, "w") as zipf:
    for fname in os.listdir(final_dir):
        zipf.write(os.path.join(final_dir, fname), arcname=fname)

print(final_zip_path)
