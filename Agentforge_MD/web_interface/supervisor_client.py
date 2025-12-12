
import requests
import json
import logging
import base64

# Configuration
RELAY_URL = "http://100.111.236.92:5100/agentforge"
INBOX_ENDPOINT = f"{RELAY_URL}/inbox/supervisor"
OUTBOX_ENDPOINT = f"{RELAY_URL}/outbox/chatgpt"

logger = logging.getLogger("AntigravitySupervisorClient")

class AntigravitySupervisorClient:
    def __init__(self):
        self.session = requests.Session()

    def send_command(self, action, data=None):
        if data is None:
            data = {}
        
        payload = {
            "sender": "antigravity_web",
            "payload": {
                "action": action,
                "data": data
            }
        }
        
        try:
            logger.info(f"Sending action: {action}")
            response = self.session.post(INBOX_ENDPOINT, json=payload, timeout=5)
            if response.status_code in [200, 201]:
                return {"status": "success", "message": "Command sent"}
            else:
                return {"status": "error", "message": f"HTTP {response.status_code}: {response.text}"}
        except Exception as e:
            logger.error(f"Error sending command: {e}")
            return {"status": "error", "message": str(e)}

    def poll_responses(self):
        try:
            response = self.session.get(OUTBOX_ENDPOINT, timeout=5)
            if response.status_code == 200:
                data = response.json()
                messages = data.get("messages", [])
                processed_msgs = []
                
                for msg in messages:
                    processed = self._process_message(msg)
                    if processed:
                        processed_msgs.append(processed)
                
                return processed_msgs
            else:
                logger.warning(f"Failed to poll outbox. Status: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Error polling responses: {e}")
            return []

    def _process_message(self, msg):
        try:
            payload_chunk = msg.get('payload_chunk', {})
            content = payload_chunk.get('content', '')
            is_base64 = payload_chunk.get('is_base64', False)
            
            decoded_data = content
            if is_base64 and content:
                try:
                    decoded = base64.b64decode(content).decode('utf-8')
                    decoded_data = json.loads(decoded)
                except Exception as e:
                    logger.error(f"Decoding error: {e}")
                    decoded_data = f"[Decode Error] {content}"

            return {
                "id": msg.get("id"),
                "timestamp": msg.get("timestamp"),
                "action": msg.get("action"),
                "sender": msg.get("sender"),
                "content": decoded_data
            }
                
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return None
