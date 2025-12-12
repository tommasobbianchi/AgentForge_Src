
import os
import json
import logging

# Configure logging
logger = logging.getLogger("InboxHandler")

class InboxHandler:
    def __init__(self, inbox_path="/opt/agentforge-relay/mailbox/inbox/supervisor"):
        self.inbox_path = inbox_path
        self._ensure_inbox_directory()

    def _ensure_inbox_directory(self):
        """Ensures that the inbox directory exists."""
        if not os.path.exists(self.inbox_path):
            try:
                os.makedirs(self.inbox_path, exist_ok=True)
                logger.info(f"Created inbox directory at: {self.inbox_path}")
            except OSError as e:
                logger.error(f"Failed to create inbox directory {self.inbox_path}: {e}")

    def fetch_messages(self):
        """
        Reads all messages from the inbox, returns them, and deletes the files.
        """
        if not os.path.exists(self.inbox_path):
            logger.warning(f"Inbox path {self.inbox_path} does not exist.")
            return []

        messages = []
        try:
            files = sorted(os.listdir(self.inbox_path))
            for filename in files:
                if not filename.endswith(".json"):
                    continue
                    
                file_path = os.path.join(self.inbox_path, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        messages.append(data)
                    
                    # Remove the file after successful read
                    os.remove(file_path)
                    logger.debug(f"Processed and removed message file: {filename}")
                except Exception as e:
                    logger.error(f"Failed to process message file {filename}: {e}")
                    
        except Exception as e:
            logger.error(f"Error listing inbox content: {e}")

        return messages
