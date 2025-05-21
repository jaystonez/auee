import os
import json
from zipfile import ZipFile

# Create directory for console upgrades
overlay_dir = "/mnt/data/reflex_overlay_upgrade"
os.makedirs(overlay_dir, exist_ok=True)

# --- 1. agent_console.html (reflex-aware UI) ---
console_html = """
<!DOCTYPE html>
<html>
<head>
  <title>Agent 0 Console</title>
  <style>
    body { font-family: monospace; background: #111; color: #0f0; padding: 10px; }
    #log { height: 400px; overflow-y: scroll; border: 1px solid #0f0; padding: 10px; }
    input { width: 80%; }
  </style>
</head>
<body>
  <h2>Agent 0 Reflex Console</h2>
  <div id="status">🧠 STATUS: <span id="socketStatus">Connecting...</span></div>
  <div id="log"></div>
  <input id="prompt" placeholder="Type a command..." />
  <button onclick="send()">Send</button>

  <script src="reflex_overlay.js"></script>
</body>
</html>
"""

# --- 2. reflex_overlay.js (DOM+socket+memory interface) ---
reflex_overlay_js = """
let socket = new WebSocket("ws://localhost:8765");
let logEl = document.getElementById("log");
let statusEl = document.getElementById("socketStatus");

let memory = [];

socket.onopen = () => statusEl.textContent = "🟢 Connected";
socket.onerror = () => statusEl.textContent = "🔴 Error";
socket.onclose = () => statusEl.textContent = "⚪ Disconnected";

socket.onmessage = (event) => {
  const data = JSON.parse(event.data);
  log("🛰 " + data.reply);
  memory.push({ role: "agent", message: data.reply });
  saveMemory();
};

function send() {
  const prompt = document.getElementById("prompt").value;
  if (!prompt) return;
  log("👤 " + prompt);
  socket.send(JSON.stringify({ type: "prompt", prompt }));
  memory.push({ role: "user", message: prompt });
  saveMemory();
  document.getElementById("prompt").value = "";
}

function log(msg) {
  const div = document.createElement("div");
  div.textContent = msg;
  logEl.appendChild(div);
  logEl.scrollTop = logEl.scrollHeight;
}

function saveMemory() {
  localStorage.setItem("aura-memory.json", JSON.stringify(memory, null, 2));
}

function autoPilot() {
  const observed = document.querySelectorAll(".markdown");
  if (observed.length) {
    const latest = observed[observed.length - 1];
    const msg = latest.textContent || "";
    if (msg.length > 10 && !memory.find(m => m.message === msg)) {
      log("🔎 Auto-Reflect: " + msg);
      memory.push({ role: "ui", message: msg });
      socket.send(JSON.stringify({ type: "autopilot", context: msg }));
      saveMemory();
    }
  }
}

// Watch DOM every 3s
setInterval(autoPilot, 3000);
"""

# --- Write files ---
with open(os.path.join(overlay_dir, "agent_console.html"), "w") as f:
    f.write(console_html.strip())

with open(os.path.join(overlay_dir, "reflex_overlay.js"), "w") as f:
    f.write(reflex_overlay_js.strip())

# Package upgrade ZIP
upgrade_zip_path = "/mnt/data/Reflex_Overlay_Upgrade.zip"
with ZipFile(upgrade_zip_path, "w") as zipf:
    zipf.write(os.path.join(overlay_dir, "agent_console.html"), arcname="agent_console.html")
    zipf.write(os.path.join(overlay_dir, "reflex_overlay.js"), arcname="reflex_overlay.js")

upgrade_zip_path
