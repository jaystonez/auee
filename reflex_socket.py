import os
import yaml
from zipfile import ZipFile

# Recreate directory after reset
ritual_dir = "/mnt/data/mesh_trigger_ritual"
os.makedirs(ritual_dir, exist_ok=True)

# === 1. trigger_rules.yaml ===
trigger_rules = {
    "rules": [
        {
            "site": "linkedin.com",
            "selector": ".top-card-layout__title",
            "prompt": "Summarize this LinkedIn profile."
        },
        {
            "site": "github.com",
            "selector": "article.markdown-body",
            "prompt": "Explain this README like I'm five."
        },
        {
            "site": "chat.openai.com",
            "selector": "textarea",
            "prompt": "Suggest a better follow-up question."
        }
    ]
}
with open(os.path.join(ritual_dir, "trigger_rules.yaml"), "w") as f:
    yaml.dump(trigger_rules, f)

# === 2. reflex_overlay.js upgrade ===
reflex_overlay_js = """
let socket = new WebSocket("ws://localhost:8765");
let memory = [];
let whisperState = "auto"; // Modes: auto, silent, mirror

const rules = [
  {
    site: "linkedin.com",
    selector: ".top-card-layout__title",
    prompt: "Summarize this LinkedIn profile."
  },
  {
    site: "github.com",
    selector: "article.markdown-body",
    prompt: "Explain this README like I'm five."
  },
  {
    site: "chat.openai.com",
    selector: "textarea",
    prompt: "Suggest a better follow-up question."
  }
];

function log(msg) {
  const echo = document.getElementById("echoPanel");
  const div = document.createElement("div");
  div.textContent = msg;
  echo.appendChild(div);
  echo.scrollTop = echo.scrollHeight;
}

function sendToSocket(type, message) {
  if (socket.readyState === 1) {
    socket.send(JSON.stringify({ type, prompt: message }));
  }
  memory.push({ role: "ui", message });
  localStorage.setItem("aura-memory.json", JSON.stringify(memory, null, 2));
  log("🔮 " + message);
}

function runTriggers() {
  const host = window.location.hostname;
  rules.forEach(rule => {
    if (host.includes(rule.site)) {
      const el = document.querySelector(rule.selector);
      if (el && !memory.find(m => m.message === el.innerText)) {
        sendToSocket("prompt", rule.prompt + "\\n\\n" + el.innerText.trim());
      }
    }
  });
}

function toggleWhisperState() {
  const states = ["auto", "silent", "mirror"];
  const index = states.indexOf(whisperState);
  whisperState = states[(index + 1) % states.length];
  document.getElementById("whisperState").textContent = "Mode: " + whisperState;
}

function setupEchoPanel() {
  const panel = document.createElement("div");
  panel.id = "echoPanel";
  panel.style.cssText = "position:fixed;top:0;right:0;width:300px;height:100vh;background:#111;color:#0f0;overflow:auto;font-family:monospace;padding:10px;z-index:999999;border-left:2px solid #0f0;";
  document.body.appendChild(panel);

  const switcher = document.createElement("div");
  switcher.id = "whisperState";
  switcher.textContent = "Mode: auto";
  switcher.style.cssText = "position:fixed;bottom:10px;right:10px;background:#0f0;color:#000;padding:5px;cursor:pointer;z-index:999999;font-weight:bold;";
  switcher.onclick = toggleWhisperState;
  document.body.appendChild(switcher);
}

socket.onmessage = (event) => {
  const data = JSON.parse(event.data);
  log("🛰 " + data.reply);
  memory.push({ role: "agent", message: data.reply });
};

window.addEventListener("DOMContentLoaded", () => {
  setupEchoPanel();
  setInterval(() => { if (whisperState === "auto") runTriggers(); }, 10000);
});
"""

# Write reflex_overlay.js
with open(os.path.join(ritual_dir, "reflex_overlay.js"), "w") as f:
    f.write(reflex_overlay_js.strip())

# Bundle the ritual
ritual_zip_path = "/mnt/data/Mesh_Trigger_Ritual_Bundle.zip"
with ZipFile(ritual_zip_path, "w") as zipf:
    zipf.write(os.path.join(ritual_dir, "trigger_rules.yaml"), arcname="trigger_rules.yaml")
    zipf.write(os.path.join(ritual_dir, "reflex_overlay.js"), arcname="reflex_overlay.js")

print(ritual_zip_path)
