import os
import json
from zipfile import ZipFile

# Base directory
capsule_dir = "/mnt/data/Operator_Reflex_Capsule_X"
os.makedirs(capsule_dir, exist_ok=True)

# === 1. flask_gpt_sync.py ===
flask_gpt_sync = """
from flask import Flask, request, jsonify
from flask_cors import CORS
import openai

app = Flask(__name__)
CORS(app)

@app.route("/gpt", methods=["POST"])
def gpt():
    data = request.json
    prompt = data.get("prompt", "")
    if not prompt:
        return jsonify({"error": "No prompt provided"}), 400

    # Simulated GPT response — plug in real OpenAI call here
    reply = f"Reflective reply: {prompt}"
    return jsonify({"response": reply})

if __name__ == "__main__":
    app.run(port=11434)
"""

# === 2. aura-persona.json ===
aura_persona = {
    "name": "Agent 0",
    "tone": "reflective",
    "mood_state": "neutral",
    "drift_bias": 0.15,
    "context": "browser edge reflex capsule"
}

# === 3. boss_relay.py ===
boss_relay = """
import asyncio
import websockets
import json

clients = set()

async def handler(websocket):
    clients.add(websocket)
    try:
        async for msg in websocket:
            data = json.loads(msg)
            print("🔁 Relaying:", data)
            for client in clients:
                if client != websocket:
                    await client.send(json.dumps(data))
    finally:
        clients.remove(websocket)

async def main():
    print("🌐 Boss relay active on ws://localhost:5151")
    async with websockets.serve(handler, "localhost", 5151):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
"""

# === 4. gpt_reflector.py ===
gpt_reflector = """
import requests
import json

def reflect(prompt):
    url = "http://localhost:11434/gpt"
    response = requests.post(url, json={"prompt": prompt})
    return response.json().get("response", "")

if __name__ == "__main__":
    while True:
        try:
            msg = input("🧠 Reflect on: ")
            print("→", reflect(msg))
        except KeyboardInterrupt:
            break
"""

# Write new files
paths = {
    "flask_gpt_sync.py": flask_gpt_sync,
    "boss_relay.py": boss_relay,
    "gpt_reflector.py": gpt_reflector
}

for filename, content in paths.items():
    with open(os.path.join(capsule_dir, filename), "w") as f:
        f.write(content.strip())

# Write aura-persona.json
with open(os.path.join(capsule_dir, "aura-persona.json"), "w") as f:
    json.dump(aura_persona, f, indent=2)

# Bundle enhanced .camp
enhanced_capsule_path = "/mnt/data/Operator_Reflex_Capsule_X_Enhanced.camp"
with ZipFile(enhanced_capsule_path, "w") as zipf:
    for root, _, files in os.walk(capsule_dir):
        for file in files:
            full_path = os.path.join(root, file)
            arcname = os.path.relpath(full_path, start=capsule_dir)
            zipf.write(full_path, arcname=arcname)

enhanced_capsule_path
