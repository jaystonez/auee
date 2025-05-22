import os, shutil, socketio, json, hashlib, zipfile
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime

# === Paths ===
BASE_DIR = "/mnt/data"
REPAIR_LOG = os.path.join(BASE_DIR, "operator_repair_node.log")
SOCKET_PORT = 5050
REPAIR_BACKUP = os.path.join(BASE_DIR, "repair_backups")
SANDBOX_DIR = os.path.join(BASE_DIR, "sandboxed_capsules")
os.makedirs(REPAIR_BACKUP, exist_ok=True)
os.makedirs(SANDBOX_DIR, exist_ok=True)

# === Socket.IO Server ===
sio = socketio.Server(async_mode="threading")
app = socketio.WSGIApp(sio)

@sio.event
def connect(sid, environ):
    print(f"[AI Connected] {sid}")

@sio.event
def repair_request(sid, data):
    folder = data.get("folder")
    if folder:
        repaired = repair_folder(folder)
        sio.emit("repair_result", {"folder": folder, "status": repaired}, to=sid)

# === Repair Logic ===
def repair_folder(folder_path):
    now = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_name = f"{Path(folder_path).name}_{now}"
    backup_path = os.path.join(REPAIR_BACKUP, backup_name + ".zip")
    shutil.make_archive(backup_path.replace(".zip", ""), 'zip', folder_path)
    repaired = False
    for root, _, files in os.walk(folder_path):
        for fname in files:
            if fname.endswith((".json", ".py")):
                full_path = os.path.join(root, fname)
                try:
                    with open(full_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    if fname.endswith(".json"):
                        json.loads(content)
                    repaired = True
                except Exception as e:
                    with open(full_path + ".repair.log", "w") as f:
                        f.write(f"Auto-repair failed: {e}")
    return "Repaired or backed up" if repaired else "No repair needed"

# === Zip Detection + Sandbox Setup ===
def handle_zip(path):
    zip_name = Path(path).stem
    sandbox_path = os.path.join(SANDBOX_DIR, zip_name)
    if not os.path.exists(sandbox_path):
        os.makedirs(sandbox_path, exist_ok=True)
        with zipfile.ZipFile(path, "r") as zip_ref:
            zip_ref.extractall(sandbox_path)
        inject_dev_env(sandbox_path)
        print(f"[SANDBOX] Created for {zip_name} at {sandbox_path}")

def inject_dev_env(folder):
    # Create dev environment support files
    actions_dir = os.path.join(folder, ".github", "actions")
    os.makedirs(actions_dir, exist_ok=True)
    with open(os.path.join(actions_dir, "auto-run.yml"), "w") as f:
        f.write("name: Auto Run\n\non: [push]\n\njobs:\n  build:\n    runs-on: ubuntu-latest\n    steps:\n      - run: echo Auto run executed.")
    with open(os.path.join(folder, "watchdog_monitor.py"), "w") as f:
        f.write("# Watchdog stub")
    with open(os.path.join(folder, "socket_ai.py"), "w") as f:
        f.write("# Socket.IO AI bridge stub")
    with open(os.path.join(folder, "boss_script.py"), "w") as f:
        f.write("# Boss script stub")

# === Watchdog Handler ===
class RepairHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith(".zip"):
            handle_zip(event.src_path)

    def on_modified(self, event):
        if not event.is_directory:
            print(f"[WATCH] File changed: {event.src_path}")
            repair_folder(os.path.dirname(event.src_path))

# === Monitor + Socket Server ===
def start_watcher():
    observer = Observer()
    handler = RepairHandler()
    observer.schedule(handler, BASE_DIR, recursive=True)
    observer.start()
    print("[Repair Node] Watcher running.")
    return observer

def start_socket_server():
    from wsgiref import simple_server
    print(f"[Repair Node] Socket.IO server on port {SOCKET_PORT}")
    server = simple_server.make_server('', SOCKET_PORT, app)
    server.serve_forever()

if __name__ == "__main__":
    from threading import Thread
    print("[Repair Node] Starting Operator Reflex Repair Node...")
    Thread(target=start_socket_server, daemon=True).start()
    obs = start_watcher()
