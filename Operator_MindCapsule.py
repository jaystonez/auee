import zipfile
import os

# Re-define paths after environment reset
capsule_dir = "/mnt/data/Operator_MindCapsule"
os.makedirs(capsule_dir, exist_ok=True)

# Define all component files again
components = {
    "memory_replay.js": """// Reads memory from .aura-memory.json and builds a replay UI
async function loadMemory() {
  const response = await fetch('/memory/.aura-memory.json');
  const memory = await response.json();
  const container = document.getElementById('memory-timeline');
  memory.entries.forEach(entry => {
    const div = document.createElement('div');
    div.innerText = `${entry.timestamp}: ${entry.text}`;
    div.onclick = () => replayReflex(entry.text);
    container.appendChild(div);
  });
}
function replayReflex(text) {
  console.log('Replaying:', text);
  // Send text to socket or trigger event
}
""",

    "trigger_voice.js": """// Hotword detection via Web Speech API
const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
recognition.continuous = true;
recognition.onresult = function(event) {
  const transcript = event.results[event.results.length - 1][0].transcript.trim();
  if (/agent 0 wake up/i.test(transcript)) {
    console.log("Hotword detected: Agent 0 wake up");
    triggerReflex("wake");
  }
};
function triggerReflex(command) {
  console.log("Triggering reflex:", command);
  // Integration point for reflex invocation
}
recognition.start();
""",

    "trigger_camera.js": """// Placeholder: hooks webcam and monitors basic motion
navigator.mediaDevices.getUserMedia({ video: true }).then(stream => {
  const video = document.createElement('video');
  video.srcObject = stream;
  video.play();
  document.body.appendChild(video);
  console.log("Camera active - placeholder motion detection online.");
}).catch(err => console.error("Camera access denied:", err));
""",

    "aura-dashboard.html": """<!DOCTYPE html>
<html>
<head><title>Aura Dashboard</title></head>
<body>
  <h1>Operator Aura Dashboard</h1>
  <input type="file" id="campDrop" />
  <button onclick="manualTrigger()">Trigger Prompt</button>
  <div id="memory-timeline"></div>
  <script src="memory_replay.js"></script>
  <script src="trigger_voice.js"></script>
  <script src="trigger_camera.js"></script>
  <script>
    loadMemory();
    function manualTrigger() {
      const text = prompt("Enter prompt:");
      triggerReflex(text);
    }
  </script>
</body>
</html>
""",

    "reflect.yaml": """capabilities:
  - inject_chatgpt_prompt
  - read_gpt_response
  - extension_socket_sync
  - qr_invocation_ready
  - memory_log
  - voice_trigger
  - camera_trigger
  - dashboard_control
"""
}

# Write each component file into the capsule directory
for filename, content in components.items():
    with open(os.path.join(capsule_dir, filename), "w", encoding="utf-8") as f:
        f.write(content)

# Create final .camp ZIP file
camp_path = "/mnt/data/Operator_MindCapsule.camp"
with zipfile.ZipFile(camp_path, 'w', zipfile.ZIP_DEFLATED) as camp_zip:
    for root, dirs, files in os.walk(capsule_dir):
        for file in files:
            file_path = os.path.join(root, file)
            arcname = os.path.relpath(file_path, capsule_dir)
            camp_zip.write(file_path, arcname=arcname)

camp_path
