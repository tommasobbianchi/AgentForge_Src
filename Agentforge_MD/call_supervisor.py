#!/usr/bin/env python3
import sys
import json
import uuid
import time
import requests
import argparse
import logging
import base64

# Configuration
RELAY_URL = "http://100.111.236.92:5101/agentforge"
INBOX_ENDPOINT = f"{RELAY_URL}/inbox/supervisor" # Fallback mainly, code uses target specific
OUTBOX_ENDPOINT = f"{RELAY_URL}/outbox/chatgpt"
TIMEOUT_SECONDS = 30
POLL_INTERVAL = 1

# Configure logging to stderr so stdout is clean for piping
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s', stream=sys.stderr)
logger = logging.getLogger("CallSupervisor")

def send_command(target_agent, session_id, action, data):
    payload = {
        "sender": session_id, 
        "recipient": target_agent, 
        "payload": {
            "action": action,
            "data": data,
            "goal": data.get("goal")
        }
    }
    
    target_inbox = f"{RELAY_URL}/inbox/{target_agent}"
    
    try:
        response = requests.post(target_inbox, json=payload, timeout=5)
        response.raise_for_status()
        return True
    except Exception as e:
        logger.error(f"Failed to send command to {target_inbox}: {e}")
        return False

def poll_response(session_id):
    start_time = time.time()
    
    while time.time() - start_time < TIMEOUT_SECONDS:
        try:
            response = requests.get(OUTBOX_ENDPOINT, timeout=5)
            if response.status_code == 200:
                data = response.json()
                messages = data.get("messages", [])
                
                for msg in messages:
                    processed = process_message_content(msg)
                    if processed:
                        if processed.get('timestamp', 0) > start_time:
                             return processed

            time.sleep(POLL_INTERVAL)
            
        except Exception as e:
            logger.error(f"Polling error: {e}")
            time.sleep(POLL_INTERVAL)
            
    return None

def process_message_content(msg):
    try:
        payload_chunk = msg.get('payload_chunk', {})
        content = payload_chunk.get('content', '')
        is_base64 = payload_chunk.get('is_base64', False)
        
        decoded_data = content
        if is_base64 and content:
            decoded = base64.b64decode(content).decode('utf-8')
            try:
                decoded_data = json.loads(decoded)
            except:
                pass
                
        return {
            "timestamp": msg.get("timestamp"),
            "action": msg.get("action"),
            "result": decoded_data
        }
    except:
        return None

def main():
    parser = argparse.ArgumentParser(description='Call AgentForge Agent')
    parser.add_argument('agent', help='Target agent (supervisor, executor, planner)')
    parser.add_argument('action', help='Action/Goal (e.g., heartbeat, "Write code")')
    parser.add_argument('data', nargs='?', default='{}', help='JSON data payload')
    
    args = parser.parse_args()
    
    try:
        if args.data.startswith("{"):
            data_dict = json.loads(args.data)
        else:
            data_dict = {"content": args.data}
    except json.JSONDecodeError:
        data_dict = {"content": args.data}

    if args.agent == 'planner':
        data_dict["goal"] = args.action
        
    session_id = f"cli_{uuid.uuid4().hex[:8]}"
    
    if send_command(args.agent, session_id, args.action, data_dict):
        result = poll_response(session_id)
        if result:
            print(json.dumps(result, indent=2))
        else:
            logger.error("Timeout waiting for response")
            sys.exit(1)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
