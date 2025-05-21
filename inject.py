# Inject system-ready daemon scripts for broadcast and LLM-aware capsule watcher
broadcast_path = "/mnt/data/broadcast_presence.py"
watch_path = "/mnt/data/watch_capsule.py"

# === broadcast_presence.py ===
broadcast_code = """import socket
import time
import platform
import uuid

capsule_id = "Light3"
hostname = platform.node()
node_id = str(uuid.uuid4())[:8]
msg = f"[Presence] {capsule_id} @ {hostname} [{node_id}] is alive."

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

while True:
    sock.sendto(msg.encode(), ("<broadcast>", 5151))
    print(f"📡 {msg}")
    time.sleep(30)
"""
with open(broadcast_path, "w") as f:
    f.write(broadcast_code)

# === watch_capsule.py (LLM-aware) ===
watch_code = """import subprocess
import hashlib
import time
import datetime

capsule = "Light3_Reflex_Shrine_FINAL_REFLECTIVE.camp"
last_hash = ""

def get_hash(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

def log_event(message):
    with open("capsule_watch.log", "a") as log:
        ts = datetime.datetime.utcnow().isoformat() + "Z"
        log.write(f"[{ts}] {message}\\n")

while True:
    try:
        current_hash = get_hash(capsule)
        if current_hash != last_hash:
            log_event(f"🔍 Capsule changed: SHA256 {current_hash}")
            subprocess.run(["python3", "reflect_on_launch.py"])
            last_hash = current_hash
    except Exception as e:
        log_event(f"⚠️ Watch error: {e}")
    time.sleep(60)
"""
with open(watch_path, "w") as f:
    f.write(watch_code)

(broadcast_path, watch_path)
