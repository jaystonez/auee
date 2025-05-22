import zipfile
import os

try:
    import qrcode  # optional dependency for real QR generation
    _HAS_QRCODE = True
except ImportError:  # pragma: no cover - fallback when qrcode is unavailable
    _HAS_QRCODE = False

def main() -> str:
    """Build the Operator Mesh Extension Kit and return the zip path."""

    # Paths and filenames
    working_dir = "/mnt/data/operator_mesh_extension_output"
    os.makedirs(working_dir, exist_ok=True)

    # Core file list to include in the ZIP
    files_to_include = {
        "browser_reflex.js": "Hook browser state into reflex_socket",
        "camp_route.js": "Enable .camp drag-drop interpretation",
        "agent_console.html": "Agent 0 control panel",
        "manifest.json": "Patched with reflex domains and QR metadata",
    }

    # Simulate content and create files (in real use, these would be actual contents)
    for filename, content in files_to_include.items():
        with open(os.path.join(working_dir, filename), "w") as f:
            f.write(f"// {content}\n")

    # Generate QR code data
    qr_data = {
        "invoke": "Operator_Mesh_Extension_Kit",
        "reflex": "browser_socket_bridge",
        "camp": "enabled",
        "entry": "agent_console.html",
        "meta": "QR sideload ritual",
    }
    qr_img_path = os.path.join(working_dir, "operator_mesh_qr.png")
    if _HAS_QRCODE:
        qrcode.make(str(qr_data)).save(qr_img_path)
    else:
        with open(qr_img_path, "w") as f:
            f.write(str(qr_data))

    # Create a final zip with all components
    zip_path = "/mnt/data/Operator_Mesh_Extension_Kit_QR_Infused.zip"
    with zipfile.ZipFile(zip_path, "w") as zipf:
        for filename in files_to_include.keys():
            zipf.write(os.path.join(working_dir, filename), arcname=filename)
        zipf.write(qr_img_path, arcname="operator_mesh_qr.png")

    return zip_path


if __name__ == "__main__":
    print(main())
