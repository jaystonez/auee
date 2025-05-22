#!/bin/bash
echo "⚙️ Booting Capsule Dev Shell Kit..."
python3 capsule_auditor.py --audit-only
if [ -f dashboard_server.py ]; then
    python3 dashboard_server.py &
fi
