
from supervisor_core.outbox_handler import OutboxHandler
from supervisor_core.inbox_handler import InboxHandler
import logging

logger = logging.getLogger("MessageBus")

class MessageBus:
    def __init__(self):
        self.outbox = OutboxHandler()
        self.inbox = InboxHandler()

    def pull(self, target="supervisor"):
        # Reads from Inbox
        # target argument is ignored as InboxHandler is configured for 'supervisor' inbox
        return self.inbox.fetch_messages()

    def push(self, target, payload):
        # Writes to Outbox
        # We assume target is 'chatgpt' or compatible with the single OutboxHandler we have.
        
        action = payload.get("action", "response")
        # We pass the entire payload as data so the receiver has full context
        # sender is 'supervisor'
        
        try:
            return self.outbox.send_message(action=action, data=payload, sender="supervisor")
        except Exception as e:
            logger.error(f"MessageBus Push Error: {e}")
            return False
