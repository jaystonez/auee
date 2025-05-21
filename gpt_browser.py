import zipfile
import os
import hashlib

SHRINE_PATH = "gpt_import/Operator_Overlay_Shrine_Ready.zip"

def validate_shrine(zip_path):
    print("[Shrine] Verifying .zip integrity...")
    if not os.path.exists(zip_path):
        print("⚠️ Shrine ZIP not found.")
        return False

    with open(zip_path, "rb") as f:
        content = f.read()
        sha256_hash = hashlib.sha256(content).hexdigest()
        print(f"[Shrine] SHA256: {sha256_hash}")

    return True

def load_shrine_capsule(zip_path):
    print("[Shrine] Loading capsule contents...")
    with zipfile.ZipFile(zip_path, 'r') as shrine:
        print("[Shrine] Files found:")
        for name in shrine.namelist():
            print(" -", name)
        shrine.extractall("gpt_import/shrine_loaded")
        print("[Shrine] Capsule extracted to /shrine_loaded")

# Main routine to mount shrine
def mount_operator_overlay():
    if validate_shrine(SHRINE_PATH):
        load_shrine_capsule(SHRINE_PATH)
        print("[Shrine] Operator Overlay is now staged and extractable.")
    else:
        print("[Shrine] Invalid or missing capsule.")

# Call it on extension load or inject manually
if __name__ == "__main__":
    mount_operator_overlay()
