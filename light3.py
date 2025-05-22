import os
from zipfile import ZipFile

# Setup directory
socket_dir = "/mnt/data/reflex_socket_fused"
os.makedirs(socket_dir, exist_ok=True)

# --- reflex_socket.py ---
reflex_socket_py = """
import asyncio
import websockets
import json

memory_log = []

async def handler(websocket):
    print("⚡ Socket connected.")
    async for message in websocket:
        try:
            data = json.loads(message)
            if data.get("type") == "prompt":
                response = await respond_to(data["prompt"])
                memory_log.append({"role": "user", "message": data["prompt"]})
                memory_log.append({"role": "agent", "message": response})
                await websocket.send(json.dumps({"reply": response}))
            elif data.get("type") == "autopilot":
                ctx = data["context"]
                memory_log.append({"role": "ui", "message": ctx})
                response = await respond_to("Reflect on: " + ctx)
                memory_log.append({"role": "agent", "message": response})
                await websocket.send(json.dumps({"reply": response}))
        except Exception as e:
            await websocket.send(json.dumps({"reply": f"[ERROR] {str(e)}"}))

async def respond_to(prompt):
    # Replace this with a real local model or API call
    print(f"🔮 GPT Reflex Triggered: {prompt}")
    return f"(Reflecting): {prompt}"

async def main():
    print("🌐 Reflex Socket Active on ws://localhost:8765")
    async with websockets.serve(handler, "localhost", 8765):
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())
"""

# Write reflex_socket.py
socket_path = os.path.join(socket_dir, "reflex_socket.py")
with open(socket_path, "w") as f:
    f.write(reflex_socket_py.strip())

# Package it
socket_zip_path = "/mnt/data/Reflex_Socket_Fused.zip"
with ZipFile(socket_zip_path, "w") as zipf:
    zipf.write(socket_path, arcname="reflex_socket.py")

print(socket_zip_path)
