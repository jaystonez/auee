import os
import hashlib

def get_file_hash(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()

def main():
    repo_root = os.path.dirname(os.path.abspath(__file__))
    file_hashes = {}
    empty_files = []
    duplicates = {}

    for root, _, files in os.walk(repo_root):
        # skip .git directory
        if '.git' in root.split(os.sep):
            continue
        for fname in files:
            path = os.path.join(root, fname)
            rel = os.path.relpath(path, repo_root)
            if os.path.getsize(path) == 0:
                empty_files.append(rel)
                continue
            file_hash = get_file_hash(path)
            duplicates.setdefault(file_hash, []).append(rel)

    dup_list = [paths for paths in duplicates.values() if len(paths) > 1]

    if empty_files:
        print('Empty files:')
        for ef in empty_files:
            print('  -', ef)
    else:
        print('No empty files found.')

    if dup_list:
        print('\nPossible duplicates (same SHA256):')
        for paths in dup_list:
            print('  -', ', '.join(paths))
    else:
        print('\nNo duplicate files found.')

if __name__ == '__main__':
    main()
