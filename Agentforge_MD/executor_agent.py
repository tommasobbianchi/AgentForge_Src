
import os
import json
import time
import uuid
import requests
import logging

# Configuration
AGENT_NAME = "executor"
RELAY_BASE = "/opt/agentforge_relay/mailbox"
INBOX_PATH = os.path.join(RELAY_BASE, "inbox", AGENT_NAME)
OUTBOX_PATH = os.path.join(RELAY_BASE, "outbox", AGENT_NAME)
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "mistral"
POLL_INTERVAL = 2

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("ExecutorAgent")

class ExecutorAgent:
    def __init__(self):
        self._ensure_directories()
        
    def _ensure_directories(self):
        os.makedirs(INBOX_PATH, exist_ok=True)
        os.makedirs(OUTBOX_PATH, exist_ok=True)
        
    def run(self):
        logger.info(f"Executor Agent {AGENT_NAME} started. Listening on {INBOX_PATH}...")
        while True:
            try:
                self.check_inbox()
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
            time.sleep(POLL_INTERVAL)
            
    def check_inbox(self):
        files = sorted([f for f in os.listdir(INBOX_PATH) if f.endswith(".json")])
        for filename in files:
            file_path = os.path.join(INBOX_PATH, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    message = json.load(f)
                
                logger.info(f"Processing message: {filename}")
                self.process_message(message)
                
                os.remove(file_path)
            except Exception as e:
                logger.error(f"Failed to process {filename}: {e}")
                
    def process_message(self, message):
        # Extract payload. 
        # Standard envelope: { "sender": "...", "payload": { "action": "...", "data": "..." } }
        # Or simplified.
        
        sender = message.get("sender", "unknown")
        payload = message.get("payload", {})
        
        # If payload is wrapped in 'payload_chunk' (from supervisor/relay normalization)
        # We might need to handle that. But for now assuming direct JSON.
        # But if coming from another agent via Relay remote, it might come raw.
        # Let's handle generic 'prompt' or 'instruction'.
        
        prompt = ""
        if isinstance(payload, str):
            prompt = payload
        elif isinstance(payload, dict):
            prompt = payload.get("data", {}).get("prompt") or payload.get("data") or str(payload)
        
        if not prompt:
            logger.warning("No prompt found in message.")
            return

        logger.info(f"Generating response for prompt: {prompt[:50]}...")
        response_text = self.call_llm(prompt)
        
        self.send_response(sender, response_text, message.get("id"))

    def call_llm(self, prompt):
        try:
            payload = {
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False
            }
            res = requests.post(OLLAMA_URL, json=payload, timeout=300)
            if res.status_code == 200:
                return res.json().get("response", "")
            else:
                return f"[Error] LLM returned status {res.status_code}"
        except Exception as e:
            return f"[Error] processing LLM request: {e}"

    def send_response(self, target, content, original_id):
        # Write to outbox. filename: timestamp_uuid.json
        msg_id = str(uuid.uuid4())
        timestamp = time.time()
        
        envelope = {
            "id": msg_id,
            "timestamp": timestamp,
            "sender": AGENT_NAME,
            "recipient": target,
            "ref_id": original_id,
            "payload": {
                "result": content,
                "status": "completed"
            }
        }
        
        filename = f"{int(timestamp)}_{msg_id}.json"
        path = os.path.join(OUTBOX_PATH, filename)
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(envelope, f, indent=2)
            
        logger.info(f"Response sent to {target} (Ref: {original_id})")

if __name__ == "__main__":
    agent = ExecutorAgent()
    agent.run()
