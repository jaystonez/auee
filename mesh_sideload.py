import zipfile
import os
import shutil

# Define paths
zip_path = "/mnt/data/1.5.14_0.zip"
extract_path = "/mnt/data/1.5.14_0_extracted"

# Remove the existing extraction directory if it exists
if os.path.exists(extract_path):
    shutil.rmtree(extract_path)

# Create a fresh extraction directory
os.makedirs(extract_path, exist_ok=True)

# Extract the contents of the ZIP file
with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    zip_ref.extractall(extract_path)

# Gather file structure summary
file_structure = []
for root, dirs, files in os.walk(extract_path):
    for file in files:
        relative_path = os.path.relpath(os.path.join(root, file), extract_path)
        file_structure.append(relative_path)

# Display the first 50 entries for brevity
print(file_structure[:50])
