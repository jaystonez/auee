#!/bin/bash
set -e

CAPSULE_DIR="$(pwd)"
REQUIREMENTS="requirements.txt"
VALIDATOR="capsule_auditor.py"
PORTABLE_GPT="http://localhost:11434/gpt"

echo ""
echo "🧠 Launching Reflex Capsule Auditor..."
echo "======================================"

# 🔧 Install dependencies
echo "📦 Installing Python requirements..."
python3 -m pip install --upgrade pip
python3 -m pip install -r "$REQUIREMENTS"

# 🔍 Run validation
echo "🔍 Auditing and repairing capsules..."
python3 "$VALIDATOR"

# 🔐 SHA256 sign all .camp capsules
echo "🔐 Hashing sealed capsules..."
mkdir -p audited_capsules
for f in audited_capsules/*.camp; do
    if [ -f "$f" ]; then
        sha256sum "$f" > "$f.sig"
        echo "✅ Hashed: $f"
    fi
done

echo ""
echo "🧠 Local GPT assist (if active): $PORTABLE_GPT"
echo "✅ Complete. Output stored in: audited_capsules/"
