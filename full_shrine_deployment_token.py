import qrcode
from PIL import Image, ImageDraw, ImageFont

# === Physical Shrine Token Generator ===

# 1. QR launch glyph
qr_path = "/mnt/data/QR_ShrineToken_Capsule_Dev_Shell_Kit.png"
launch_uri = "capsule://launch/Capsule_Dev_Shell_Kit_SHRINE"
qr_img = qrcode.make(launch_uri)

# 2. Shrine Desktop Stub (.desktop launcher for Linux)
desktop_stub_path = "/mnt/data/Launch_Capsule_Shrine.desktop"
with open(desktop_stub_path, "w") as f:
    f.write(f"""[Desktop Entry]
Name=Launch Capsule Dev Shell Kit
Comment=Boots the Agent 0 Shrine Reflex Capsule
Exec=sh -c 'unzip Capsule_Dev_Shell_Kit_SHRINE.camp -d shrine && cd shrine && chmod +x __launch.sh && ./__launch.sh'
Icon=utilities-terminal
Terminal=true
Type=Application
Categories=Utility;Development;
""")

# 3. Auto-update script (re-pulls capsule from a local source or remote git)
update_script_path = "/mnt/data/update_capsule_dev_shell.sh"
with open(update_script_path, "w") as f:
    f.write("""#!/bin/bash
echo "🔄 Checking for updates to Capsule Dev Shell Kit..."
# Placeholder: Replace with real update logic (e.g. git pull or download from server)
# For now, just touch to simulate update
touch Capsule_Dev_Shell_Kit_SHRINE.camp
echo "✅ Capsule is now up to date."
""")

# Save QR
qr_img.save(qr_path)

print((qr_path, desktop_stub_path, update_script_path))
