
import os
import json
import time
import uuid
import requests
import logging

# Configuration
AGENT_NAME = "planner"
TARGET_AGENT = "executor"
RELAY_BASE = "/opt/agentforge_relay/mailbox"
INBOX_PATH = os.path.join(RELAY_BASE, "inbox", AGENT_NAME)
OUTBOX_PATH = os.path.join(RELAY_BASE, "outbox", AGENT_NAME)
TARGET_INBOX_PATH = os.path.join(RELAY_BASE, "inbox", TARGET_AGENT) # We write directly or via outbox?
# The Relay logic: Agents write to their OWN Outbox. The Relay Router moves it?
# Or Agents write to Recipient's Inbox?
# "The User's main goal is to replace the existing GPT Supervisor... interacting with AgentForge Relay."
# Relay typically moves from Outbox -> Inbox.
# BUT my `executor_agent` implementation writes to `outbox/executor`.
# How does it get to `inbox/planner`?
# Currently, there is NO active Relay process moving files between agents (Supervisor used to do it? Or Relay App?).
# The Relay App `app.py` is an HTTP API. It doesn't seem to have a background loop moving files between folders on disk.
# The `antigravity_supervisor.py` (Client) polled `outbox/chatgpt` via HTTP.
# 
# IF I want agents to communicate on the same server without a running Relay "Router" Loop, 
# I can cheat and write directly to `inbox/executor` (simulating a direct message).
# OR I rely on the existing "Supervisor Loop" to route?
# `supervisor_loop.py` pulls from `inbox/supervisor`. It doesn't route generally.
#
# SYSTEM DECISION: Since we are on `nativeserver` (local fs), `planner` will write DIRECTLY to `inbox/executor`.
# This mimics "The Network" delivering the message.

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "mistral"
POLL_INTERVAL = 2

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("PlannerAgent")

class PlannerAgent:
    def __init__(self):
        self._ensure_directories()
        
    def _ensure_directories(self):
        os.makedirs(INBOX_PATH, exist_ok=True)
        os.makedirs(OUTBOX_PATH, exist_ok=True)
        # Ensure target inbox exists so we can write to it
        os.makedirs(TARGET_INBOX_PATH, exist_ok=True)
        
    def run(self):
        logger.info(f"Planner Agent {AGENT_NAME} started. Listening on {INBOX_PATH}...")
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
        sender = message.get("sender", "unknown")
        
        # Check if it's a response from Executor
        if sender == TARGET_AGENT:
            self.handle_execution_result(message)
            return

        # Otherwise assume it's a Goal/Task from User/Supervisor
        payload = message.get("payload", {})
        goal = ""
        if isinstance(payload, dict):
            goal = payload.get("data", {}).get("goal") or payload.get("goal")
        
        if not goal:
            logger.warning("No goal found in message.")
            return

        logger.info(f"Received Goal: {goal}")
        
        # 1. PLAN
        plan_prompt = f"You are a Planner Agent. Your goal is: {goal}. Return a concise, step-by-step execution plan."
        plan = self.call_llm(plan_prompt)
        logger.info(f"Generated Plan: {plan}")
        
        # 2. DELEGATE (Sending whole plan to executor for now as a single complex task)
        # In a real system we would parse steps. Here we simply forward the "Execution" request.
        
        exec_prompt = f"You are an Executor. Here is the plan: {plan}. \n\nExecute this plan by generating the necessary code or text."
        self.send_to_agent(TARGET_AGENT, exec_prompt, message.get("id"))
        
        # We could reply to User "Plan created, sent to worker".
        self.send_response(sender, f"Plan generated and sent to {TARGET_AGENT}:\n{plan}", message.get("id"))

    def handle_execution_result(self, message):
         # Forward result to original sender? 
         # We lost context of 'original_user' unless we persisted state.
         # For this MVP, we just log it or write to a 'completed' log.
         # Or prompt LLM to summarize/evaluate.
         
         result = message.get("payload", {}).get("result", "")
         ref_id = message.get("ref_id")
         
         logger.info(f"Executor finished task {ref_id}. Result len: {len(result)}")
         
         # Assuming we want to notify the Supervisor/User
         # We don't know the Original Sender easily without state. 
         # But usually 'supervisor' is the controller.
         
         # Let's send a broadcast/notification to Supervisor inbox (which Antigravity Client reads via poll?)
         # No, Antigravity Client polls `outbox/chatgpt`.
         # The Supervisor Core logic reads `inbox/supervisor`.
         
         # To make it visible to User, we should write to `outbox/planner` (User reads this?)
         # The Web Console polls `/api/poll` -> `client.poll_responses()` -> `OUTBOX_ENDPOINT` (chatgpt).
         
         # HACK: Write to `outbox/chatgpt` so the Web Console sees it.
         # Ideally, we should use the Relay Router.
         
         SHARED_OUTBOX = os.path.join(RELAY_BASE, "outbox", "chatgpt")
         self.write_to_message_file(SHARED_OUTBOX, "planner", "supervisor", f"Execution Completed: {result}", ref_id)

    def call_llm(self, prompt):
        try:
            payload = {
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False
            }
            res = requests.post(OLLAMA_URL, json=payload, timeout=120)
            if res.status_code == 200:
                return res.json().get("response", "")
            else:
                return f"[Error] LLM returned status {res.status_code}"
        except Exception as e:
            return f"[Error] processing LLM request: {e}"

    def send_to_agent(self, target_agent_name, content, original_id):
        # Write to Target's INBOX directly
        target_path = os.path.join(RELAY_BASE, "inbox", target_agent_name)
        self.write_to_message_file(target_path, AGENT_NAME, target_agent_name, content, original_id)

    def send_response(self, target, content, original_id):
        # Reply to whoever sent (User)
        # Assuming User checks `outbox/chatgpt`. We write there.
        target_path = os.path.join(RELAY_BASE, "outbox", "chatgpt")
        self.write_to_message_file(target_path, AGENT_NAME, target, content, original_id)

    def write_to_message_file(self, folder, sender, recipient, content, ref_id):
        if not os.path.exists(folder):
            os.makedirs(folder, exist_ok=True)
            
        msg_id = str(uuid.uuid4())
        timestamp = time.time()
        
        envelope = {
            "id": msg_id,
            "timestamp": timestamp,
            "sender": sender,
            "recipient": recipient,
            "ref_id": ref_id,
            "payload_chunk": { # Mimic legacy format for Web Console compat
                "content": content, 
                "is_base64": False 
            },
            "payload": { # Standard format for agents
                "result": content
            }
        }
        
        filename = f"{int(timestamp)}_{msg_id}.json"
        path = os.path.join(folder, filename)
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(envelope, f, indent=2)
            
        logger.info(f"Message sent to {folder} (Recipient: {recipient})")

if __name__ == "__main__":
    agent = PlannerAgent()
    agent.run()
