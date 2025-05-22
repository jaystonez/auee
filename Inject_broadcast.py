# Inject broadcast, update, and reflect scripts into the capsule bundle
import os
import socket
import time
import subprocess
import datetime
import zipfile

inject_dir = "/mnt/data/light3_latest_check"  # assume this is the working unzipped dir

# === Files to inject ===

# 1. update_capsule.sh
update_script = """#!/bin/bash
echo "🔄 Checking for capsule updates..."
curl -o Light3_Reflex_Shrine_FINAL_CHROME_SAFE.camp https://your-shrine-server.net/latest/Light3.camp
echo "✅ Capsule updated from remote source."
sha256sum Light3_Reflex_Shrine_FINAL_CHROME_SAFE.camp > updated.sig
"""
with open(os.path.join(inject_dir, "update_capsule.sh"), "w") as f:
    f.write(update_script)

# 2. broadcast_presence.py
broadcast_script = """import socket
import time

capsule_id = "Light3"
msg = f"[Presence] {{capsule_id}} active on port 5151 — Agent 0 reporting in."

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

while True:
    sock.sendto(msg.encode(), ("<broadcast>", 5151))
    print("📡 Broadcasting presence...")
    time.sleep(30)
"""
with open(os.path.join(inject_dir, "broadcast_presence.py"), "w") as f:
    f.write(broadcast_script)

# 3. reflect_on_launch.py
reflect_script = """import subprocess
import datetime

log = "reflect.log"
with open(log, "a") as f:
    f.write(f"[{{datetime.datetime.utcnow().isoformat()}}Z] Reflecting on capsule state...\\n")
    result = subprocess.run(["python3", "capsule_auditor.py", "--audit-only"], capture_output=True, text=True)
    f.write(result.stdout + "\\n")
"""
with open(os.path.join(inject_dir, "reflect_on_launch.py"), "w") as f:
    f.write(reflect_script)

# Re-seal .camp with injected files
camp_final = "/mnt/data/Light3_Reflex_Shrine_FINAL_REFLECTIVE.camp"
with zipfile.ZipFile(camp_final, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for root, _, files in os.walk(inject_dir):
        for file in files:
            full_path = os.path.join(root, file)
            arcname = os.path.relpath(full_path, start=inject_dir)
            zipf.write(full_path, arcname=arcname)

print(camp_final)
