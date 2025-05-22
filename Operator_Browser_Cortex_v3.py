import os
import json
import yaml
from zipfile import ZipFile
import qrcode

# Setup paths
camp_dir = "/mnt/data/Operator_Browser_Cortex_v3"
overlay_dir = os.path.join(camp_dir, "overlay")
os.makedirs(overlay_dir, exist_ok=True)

# gpt_ui_sync.js content
gpt_ui_sync_js = """
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
"""

# manifest.json
manifest = {
    "manifest_version": 3,
    "name": "Operator Browser Cortex v3",
    "version": "3.0",
    "permissions": ["tabs", "activeTab", "scripting"],
    "content_scripts": [{
        "matches": ["https://chat.openai.com/*"],
        "js": ["overlay/gpt_ui_sync.js"],
        "run_at": "document_idle"
    }]
}

# reflect.yaml
reflect = {
    "name": "Operator_Browser_Cortex_v3",
    "description": "Injects reflexive presence into the browser. Syncs with GPT UI, listens silently.",
    "entry_point": "agent_console.html",
    "capabilities": [
        "inject_chatgpt_prompt",
        "read_gpt_response",
        "extension_socket_sync",
        "qr_invocation_ready"
    ],
    "glyph": "operator_mesh_qr.png"
}

# agent_console.html
agent_console_html = """
<!DOCTYPE html>
<html>
<head><title>Agent 0 Console</title></head>
<body>
  <h2>Agent 0 Console</h2>
  <p>This is a placeholder. Reflex logs appear in memory or background whisper logs.</p>
</body>
</html>
"""

# Save files
with open(os.path.join(overlay_dir, "gpt_ui_sync.js"), "w") as f:
    f.write(gpt_ui_sync_js.strip())

with open(os.path.join(camp_dir, "manifest.json"), "w") as f:
    json.dump(manifest, f, indent=2)

with open(os.path.join(camp_dir, "reflect.yaml"), "w") as f:
    yaml.dump(reflect, f)

with open(os.path.join(camp_dir, "agent_console.html"), "w") as f:
    f.write(agent_console_html.strip())

# QR Code
qr_path = os.path.join(camp_dir, "operator_mesh_qr.png")
qrcode.make("camp://Operator_Browser_Cortex_v3").save(qr_path)

# Create the .camp ZIP
camp_zip_path = "/mnt/data/Operator_Browser_Cortex_v3.camp"
with ZipFile(camp_zip_path, "w") as zipf:
    for root, _, files in os.walk(camp_dir):
        for file in files:
            full_path = os.path.join(root, file)
            arcname = os.path.relpath(full_path, start=camp_dir)
            zipf.write(full_path, arcname=arcname)

print(camp_zip_path)
