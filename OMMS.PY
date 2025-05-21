import os
from pathlib import Path
import hashlib

# Define the expected capsule path
camp_file_path = Path("C:/mnt/data/Light3_Reflex_Shrine_GPT_Embedded.camp")

if not camp_file_path.exists():
    print(f"❌ Capsule file not found: {camp_file_path}")
    print("➡️  Check the path or rename the file if needed.")
    exit(1)

print("✅ Capsule file found.")

# Seal hash logic
with open(camp_file_path, "rb") as f:
    data = f.read()
    sha256 = hashlib.sha256(data).hexdigest()

sig_path = camp_file_path.with_suffix(".sig")
with open(sig_path, "w", encoding="utf-8") as f:
    f.write(sha256)

print(f"🔐 SHA256 sealed: {sha256}")
print(f"📁 Signature saved to: {sig_path}")
