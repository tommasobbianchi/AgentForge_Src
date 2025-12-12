
import sys
import os
import logging
import shutil

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RemoteTest")

# Robust Import Logic
try:
    # Try package import first
    from supervisor_core.outbox_handler import OutboxHandler
    from supervisor_core.inbox_handler import InboxHandler
    from supervisor_core.policy_engine import PolicyEngine
    logger.info("Imported via supervisor_core package.")
except ImportError:
    try:
        # Try local import
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from outbox_handler import OutboxHandler
        from inbox_handler import InboxHandler
        from policy_engine import PolicyEngine
        logger.info("Imported via local path.")
    except ImportError as e:
        logger.error(f"Import failed: {e}")
        sys.exit(1)

def test_outbox():
    logger.info("Testing OutboxHandler...")
    test_outbox_path = "/tmp/agentforge_test_outbox"
    if os.path.exists(test_outbox_path):
        shutil.rmtree(test_outbox_path)
    
    # Disable auto tools for simple test unless payload triggers it
    handler = OutboxHandler(outbox_path=test_outbox_path, config={"assistant": {"auto_chunk_payloads": False, "auto_base64": False}})
    success = handler.send_message("test_action", {"foo": "bar"})
    
    if success and len(os.listdir(test_outbox_path)) > 0:
        logger.info("OutboxHandler: PASS")
    else:
        logger.error("OutboxHandler: FAIL")

def test_inbox():
    logger.info("Testing InboxHandler...")
    test_inbox_path = "/tmp/agentforge_test_inbox"
    if not os.path.exists(test_inbox_path):
        os.makedirs(test_inbox_path)
    
    # Cleanup previous run
    for f in os.listdir(test_inbox_path):
        os.remove(os.path.join(test_inbox_path, f))

    # Create dummy message
    dummy_msg = {"sender": "test", "payload": {"data": "read_me"}}
    with open(os.path.join(test_inbox_path, "msg.json"), "w") as f:
        json.dump(dummy_msg, f)
        
    handler = InboxHandler(inbox_path=test_inbox_path)
    msgs = handler.fetch_messages()
    
    if len(msgs) == 1 and msgs[0].get('payload', {}).get('data') == "read_me":
        logger.info("InboxHandler: PASS")
    else:
        logger.error(f"InboxHandler: FAIL (Got {len(msgs)} messages)")

def test_policy():
    logger.info("Testing PolicyEngine...")
    engine = PolicyEngine()
    if engine.validate("analyze_project", {}):
        logger.info("PolicyEngine: PASS")
    else:
        logger.error("PolicyEngine: FAIL")

import json

if __name__ == "__main__":
    test_outbox()
    test_inbox()
    test_policy()
