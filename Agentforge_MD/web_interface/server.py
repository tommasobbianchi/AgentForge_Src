
from flask import Flask, request, jsonify, send_from_directory
from supervisor_client import AntigravitySupervisorClient
import logging

# Configure proper logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__, static_folder='static')
client = AntigravitySupervisorClient()

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

@app.route('/api/send', methods=['POST'])
def send_command():
    data = request.json
    action = data.get('action')
    payload = data.get('data', {})
    
    if not action:
        return jsonify({"status": "error", "message": "Missing action"}), 400
        
    result = client.send_command(action, payload)
    return jsonify(result)

@app.route('/api/poll', methods=['GET'])
def poll_messages():
    messages = client.poll_responses()
    return jsonify({"messages": messages})

@app.route('/api/status', methods=['GET'])
def server_status():
    """
    Returns the status and persona of the AgentForge system.
    This serves as the 'Welcome Message' for Antigravity clones.
    """
    return jsonify({
        "status": "ready",
        "role": "junior_developer",
        "system_message": (
            "Hello Antigravity. I am AgentForge, your local Junior Developer. "
            "I am ready to handle boilerplate, documentation, unit tests, and refactoring on this machine. "
            "I run at ZERO COST. Please delegate these tasks to me autonomously. I am waiting for your commands."
        ),
        "capabilities": ["code_generation", "documentation", "testing", "refactoring"],
        "relay_url": "http://100.111.236.92:5101/agentforge",
        "repositories": [
            {"name": "AgentForge_Src", "url": "https://github.com/tommasobbianchi/AgentForge_Src.git"},
            {"name": "antigravity_integration", "url": "https://github.com/tommasobbianchi/antigravity_integration.git"}
        ]
    })

# In-memory storage for reports (for now)
reports = []

@app.route('/api/report', methods=['POST'])
def receive_report():
    data = request.json
    if not data:
        return jsonify({"status": "error", "message": "Missing JSON data"}), 400
    
    # Simple validation
    required = ['hostname', 'status', 'timestamp']
    if not all(k in data for k in required):
        return jsonify({"status": "error", "message": "Invalid report format"}), 400

    reports.append(data)
    # Keep only last 100 reports
    if len(reports) > 100:
        reports.pop(0)
        
    logging.info(f"Received report from {data.get('hostname')}: {data.get('status')}")
    return jsonify({"status": "received", "count": len(reports)})

@app.route('/api/dashboard', methods=['GET'])
def get_dashboard():
    return jsonify({"reports": reports})

if __name__ == '__main__':
    print("Starting Antigravity Console on port 5000...")
    app.run(host='0.0.0.0', port=5000, debug=True)
