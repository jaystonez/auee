import shutil
import os
import zipfile

# === Healing Light3 Mesh ===

# Define paths
source_dir = "/mnt/data/light3_contents"
output_dir = "/mnt/data/light3_shrine_bundle"
capsules_dir = os.path.join(output_dir, "capsules")
os.makedirs(capsules_dir, exist_ok=True)

# Move core launch and audit tools to root of output bundle
core_files = [
    "reflex_capsule_auditor.py", "requirements.txt", "autorun.yaml",
    "__launch.sh", "__launch.bat", "capsule_launcher.html", "reflex_debug_mode.bat",
    "Capsule_Shrine_OneClick_Launcher.html"
]

# Also include these optional capsule references
optional_capsules = [
    "Capsule_Dev_Shell_Kit_SHRINE.camp", "Operator_MindCapsule.camp"
]

# Copy all core files
for file in core_files + optional_capsules:
    src = os.path.join(source_dir, file)
    if os.path.exists(src):
        shutil.copy(src, output_dir)

# Move all capsule directories/zips into /capsules
capsule_dirs = [
    "Operator_Mesh_Sideloaded_Clean", "Operator_MindCapsule",
    "Operator_Reflex_Capsule_X", "Mesh_Trigger_Ritual_Bundle",
    "reflex_socket_fused", "reflex_overlay_upgrade",
    "pip-window", "pip-window-js", "realtime-src", "webfonts", "css", "js"
]

capsule_files = [
    "light.py", "light2.py", "light3.py", "mesh_sidloadout.py", "operator_mesh.py",
    "gpt_browser.py", "conversation_agent.js", "debugger.js", "intent_agent.js",
    "notification.js", "popup.html", "popup.js", "script.js", "socket_proxy.js",
    "sticky.js", "proxy.js", "utils.js", "socket.io.min.js", "abort-utils.js",
    "content.js", "background.js", "offscreen.js", "offscreen copy.js", "offscreen.html",
    "agent_console.html", "markdown-renderer.html", "manifest.json"
]

# Copy capsule folders and files
for item in capsule_dirs:
    src = os.path.join(source_dir, item)
    dst = os.path.join(capsules_dir, item)
    if os.path.exists(src):
        shutil.copytree(src, dst)

for file in capsule_files:
    src = os.path.join(source_dir, file)
    dst = os.path.join(capsules_dir, file)
    if os.path.exists(src):
        shutil.copy(src, dst)

# Bundle into final healed .camp
final_camp = "/mnt/data/Light3_Reflex_Shrine_Healed.camp"
with zipfile.ZipFile(final_camp, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for root, _, files in os.walk(output_dir):
        for file in files:
            full_path = os.path.join(root, file)
            arcname = os.path.relpath(full_path, start=output_dir)
            zipf.write(full_path, arcname=arcname)

final_camp
