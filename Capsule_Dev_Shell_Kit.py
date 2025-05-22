# Rebuild the ZIP first since the runtime environment was reset
import zipfile

output_zip = "/mnt/data/Capsule_Dev_Shell_Kit.zip"
files_to_include = [
    "capsule_auditor.py",
    "requirements.txt",
    "launch_capsule.sh",
    "reflex_debug_mode.bat",
    "capsule_launcher.html",
    "dashboard_server.py",
    "capsule_bundle.bat"
]

with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED) as zipf:
    for file in files_to_include:
        file_path = f"/mnt/data/{file}"
        if os.path.exists(file_path):
            zipf.write(file_path, arcname=file)

print(output_zip)
