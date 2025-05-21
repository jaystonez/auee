# Integrated Flask Application

# Advanced GPT Assistant
# ======================
# Features:
# - Real-time GPT-4 interaction via Socket.IO
# - Dynamic route configuration
# - Enhanced assistant capabilities

# Ensure monkey patching happens first
import eventlet
eventlet.monkey_patch()

import os
import openai
import logging
from flask import Flask, jsonify, request, render_template
from flask_socketio import SocketIO
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Load the API key from the environment
openai.api_key = os.getenv("API_KEY_OPENAI", "")

# Initialize Flask app and Socket.IO
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'default_secret_key')
socketio = SocketIO(app, cors_allowed_origins="*", async_mode=os.getenv('SOCKETIO_ASYNC_MODE', 'eventlet'))

# Set up logging
logging.basicConfig(level=os.getenv("LOGGING_LEVEL", "INFO"))

# Environment-based feature flags
FEATURE_BETA = os.getenv('FEATURE_BETA', 'false').lower() == 'true'
FEATURE_VIP = os.getenv('FEATURE_VIP', 'false').lower() == 'true'

# Flask Routes
@app.route('/')
def home():
    return render_template('index.html')


@app.route('/beta-feature')
def beta_feature():
    if FEATURE_BETA:
        return jsonify({"message": "Welcome to the Beta feature!"})
    else:
        return jsonify({"message": "This feature is not yet available."}), 403


@app.route('/vip')
def vip_feature():
    if FEATURE_VIP:
        return jsonify({"message": "Welcome VIP! You have access to exclusive features."})
    else:
        return jsonify({"message": "This is for VIPs only."}), 403


@app.route('/quick-connect')
def quick_connect():
    assistant = BossAssistant()
    assistant.run_all_features()
    return jsonify({"message": "🚀 All features activated!"})


@app.route('/auto-fix')
def auto_fix():
    assistant = SmartFixerAssistant()
    issue_log = "ModuleNotFoundError: No module named 'vip_feature'"
    solution = assistant.request_fix(issue_log)
    return jsonify({"solution": solution})


@app.route('/chat', methods=['POST'])
def chat():
    message = request.json.get('message')
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": message}
            ],
            temperature=0.5,
            max_tokens=150
        )
        return jsonify({"response": response.choices[0]['message']['content']})
    except Exception as e:
        logging.error(f"GPT request failed: {e}")
        return jsonify({"error": "An error occurred while processing your request."}), 500


# WebSocket Events
@socketio.on("connect")
def handle_connect():
    logging.info("Client connected")
    socketio.emit("server_message", {"message": "Socket.IO connection established!"})


@socketio.on("send_message")
def handle_message(data):
    user_message = data.get("message", "")
    logging.info(f"Message received from client: {user_message}")
    
    # Pass the user message to GPT for a response
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_message}
            ],
            temperature=0.5,
            max_tokens=150
        ).choices[0]['message']['content']
    except Exception as e:
        logging.error(f"GPT request failed: {e}")
        response = "An error occurred while processing your request."

    # Send the response back to the client
    socketio.emit("receive_message", {"response": response})
    logging.info(f"Sent GPT response: {response}")


@socketio.on("assistant_response")
def handle_assistant_response(data):
    assistant_message = data.get("message", "")
    logging.info(f"Assistant sent: {assistant_message}")
    # Optionally broadcast or log this
    socketio.emit("server_broadcast", {"response": assistant_message})


# Assistants
class SmartFixerAssistant:
    def __init__(self):
        self.VIP_MODE = os.getenv("ENABLE_VIP_MODE", "false").lower() == "true"
        self.BETA_MODE = os.getenv("ENABLE_BETA_MODE", "false").lower() == "true"
        self.EXEC_MODE = os.getenv("ENABLE_EXEC_MODE", "false").lower() == "true"

    def unlock_features(self, solution):
        if "VIP" in solution:
            self.VIP_MODE = True
            logging.info("VIP Mode unlocked!")
        if "Beta" in solution:
            self.BETA_MODE = True
            logging.info("Beta Mode unlocked!")
        if "Executive" in solution:
            self.EXEC_MODE = True
            logging.info("Executive Mode unlocked!")

    def request_fix(self, issue_log):
        prompt = f"Help solve this issue: {issue_log}"
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=150
            )
            solution = response.choices[0]['message']['content']
            logging.info(f"Suggested solution: {solution}")
            self.unlock_features(solution)
            return solution
        except Exception as e:
            logging.error(f"Error during GPT request: {e}")
            return None


class ChatGPTAssistant:
    def summarize_project(self, project_path):
        return "Project summary: files and Git status."

    def git_status(self):
        return "Current Git status."

    def docker_status(self):
        return "Docker container is running."


class BossAssistant:
    def __init__(self):
        self.VIP_MODE = os.getenv("ENABLE_VIP_MODE", "false").lower() == "true"
        self.BETA_MODE = os.getenv("ENABLE_BETA_MODE", "false").lower() == "true"
        self.EXEC_MODE = os.getenv("ENABLE_EXEC_MODE", "false").lower() == "true"

    def run_all_features(self):
        self.VIP_MODE = self.BETA_MODE = self.EXEC_MODE = True
        logging.info("All modes activated: VIP, Beta, Executive")


if __name__ == "__main__":
    socketio.run(app, debug=os.getenv("FLASK_DEBUG") == "True", host="127.0.0.1", port=int(os.getenv("FLASK_PORT", 5000)))
