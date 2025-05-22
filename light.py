import os
import json
import yaml
from zipfile import ZipFile
import qrcode

# Set up .camp directory
camp_dir = "/mnt/data/Operator_Browser_Cortex"
os.makedirs(os.path.join(camp_dir, "overlay"), exist_ok=True)

# Define script contents
scripts = {
    "gpt_ui_sync.js": """
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
""",
    "browser_reflex.js": "// Placeholder for DOM intent bridge",
    "camp_route.js": "// Placeholder for .camp drag-n-drop handling"
}

# Write overlay scripts
for name, content in scripts.items():
    with open(os.path.join(camp_dir, "overlay", name), "w") as f:
        f.write(content.strip())

# UI Console HTML
html_path = os.path.join(camp_dir, "agent_console.html")
with open(html_path, "w") as f:
    f.write("<!-- Agent 0 console placeholder -->")

# Manifest
manifest = {
    "manifest_version": 3,
    "name": "Operator Browser Cortex",
    "version": "2.0",
    "permissions": ["tabs", "activeTab", "scripting"],
    "content_scripts": [{
        "matches": ["https://chat.openai.com/*"],
        "js": ["gpt_ui_sync.js"],
        "run_at": "document_idle"
    }]
}
with open(os.path.join(camp_dir, "manifest.json"), "w") as f:
    json.dump(manifest, f, indent=2)

# Reflect.yaml
reflect_meta = {
    "name": "Operator_Browser_Cortex",
    "description": "Injects reflex presence into the browser. Syncs with ChatGPT UI, observes DOM, responds to capsules.",
    "capabilities": [
        "inject_chatgpt_prompt",
        "read_gpt_response",
        "sync_dom_events",
        "accept_camp_capsules",
        "log_to_aura_memory"
    ],
    "entry_point": "agent_console.html",
    "glyph": "operator_mesh_qr.png"
}
with open(os.path.join(camp_dir, "reflect.yaml"), "w") as f:
    yaml.dump(reflect_meta, f)

# QR code
qr_path = os.path.join(camp_dir, "operator_mesh_qr.png")
qrcode.make("camp://Operator_Browser_Cortex?entry=agent_console.html").save(qr_path)

# Zip everything into a .camp
camp_zip_path = "/mnt/data/Operator_Browser_Cortex.camp"
with ZipFile(camp_zip_path, "w") as zipf:
    for root, _, files in os.walk(camp_dir):
        for file in files:
            full_path = os.path.join(root, file)
            arcname = os.path.relpath(full_path, start=camp_dir)
            zipf.write(full_path, arcname=arcname)

print(camp_zip_path)




