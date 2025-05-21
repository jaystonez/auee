#!/bin/bash
echo "⚙️ Booting Capsule Dev Shell Kit..."
chmod +x reflex_capsule_auditor.py
python3 reflex_capsule_auditor.py --audit-only
if [ -f dashboard_server.py ]; then
    python3 dashboard_server.py &
fi
