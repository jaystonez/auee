@echo off
echo Launching Capsule Dev Shell Kit...
python capsule_auditor.py --audit-only
start dashboard_server.py
