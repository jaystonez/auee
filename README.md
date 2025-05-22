# AUEE Capsule Tools

This repository provides scripts for building and auditing **capsules**—zip-based `.camp` packages containing browser extensions or agent resources. The generated capsules can be loaded into the Light3 Shrine environment or other compatible launchers.

## Capsule generation
- `Operator_Reflex_Capsule_X.py` writes an aura persona file and packages multiple components into `Operator_Reflex_Capsule_X_Enhanced.camp`.
- `Light3_Reflex_Shrine_Healed.py` collects extension files and creates `Light3_Reflex_Shrine_Healed.camp`.
- `capsule_auditor.py` scans capsules, repairs missing metadata, and outputs a summary report.

## Dashboard server
`camp_unpack_and_run_v2.py` runs a Flask application with Socket.IO for real‑time GPT interaction. Start it with:
```bash
python camp_unpack_and_run_v2.py
```
The server listens on `http://127.0.0.1:5000`.

## Workflow
1. Install dependencies: `pip install -r requirements.txt`.
2. Run a capsule script (for example `python Operator_Reflex_Capsule_X.py`) to produce a `.camp` file in `/mnt/data/`.
3. Optionally audit capsules with `python capsule_auditor.py`.
4. Launch the dashboard via `python camp_unpack_and_run_v2.py` and open `index.html` to access the UI.

## Required packages
Key Python dependencies listed in `requirements.txt` include:
- Flask / Flask-SocketIO
- eventlet
- requests
- pyyaml
- openai
- qrcode
- pillow
- python-dotenv
