
import os
import json
import uuid
import time
import logging
import base64
import math

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("OutboxHandler")

class OutboxHandler:
    def __init__(self, outbox_path="/opt/agentforge-relay/mailbox/outbox/chatgpt", config=None):
        self.outbox_path = outbox_path
        self._ensure_outbox_directory()
        self.config = config or {}
        
        # Load config logic for chunking/base64
        # Defaulting provided for safety if config is missing
        self.chunk_size = self.config.get("relay", {}).get("chunk_size", 8192)
        self.auto_chunk = self.config.get("assistant", {}).get("auto_chunk_payloads", True)
        self.auto_base64 = self.config.get("assistant", {}).get("auto_base64", True)

    def _ensure_outbox_directory(self):
        """Ensures that the outbox directory exists."""
        if not os.path.exists(self.outbox_path):
            try:
                os.makedirs(self.outbox_path, exist_ok=True)
                logger.info(f"Created outbox directory at: {self.outbox_path}")
            except OSError as e:
                logger.error(f"Failed to create outbox directory {self.outbox_path}: {e}")

    def _process_payload(self, data):
        """
        Applies Base64 encoding and Chunking to the data dictionary.
        Returns a list of payload chunks.
        """
        # 1. Serialize data to JSON string
        json_str = json.dumps(data, ensure_ascii=False)
        
        # 2. Base64 Encode if enabled
        if self.auto_base64:
            # Encode to bytes, then base64, then decode back to info string
            encoded_bytes = base64.b64encode(json_str.encode('utf-8'))
            processed_str = encoded_bytes.decode('utf-8')
            is_base64 = True
        else:
            processed_str = json_str
            is_base64 = False

        # 3. Chunking if enabled
        chunks = []
        if self.auto_chunk and len(processed_str) > self.chunk_size:
            total_chunks = math.ceil(len(processed_str) / self.chunk_size)
            for i in range(total_chunks):
                start = i * self.chunk_size
                end = start + self.chunk_size
                chunk_content = processed_str[start:end]
                chunks.append({
                    "chunk_index": i,
                    "total_chunks": total_chunks,
                    "content": chunk_content,
                    "is_base64": is_base64
                })
        else:
            # Single chunk handling
            chunks.append({
                "chunk_index": 0,
                "total_chunks": 1,
                "content": processed_str,
                "is_base64": is_base64
            })
            
        return chunks

    def send_message(self, action: str, data: dict, sender: str = "supervisor"):
        """
        Constructs and writes a message to the outbox.
        """
        message_id = str(uuid.uuid4())
        timestamp = time.time()
        
        # Prepare the data payload (chunked/encoded)
        # Note: The 'action' usually stays as metadata, 'data' gets chunked.
        # But requirements say "wrapper unico che chunkizza payload".
        # Assuming the entire 'data' dict is the payload to chunk.
        
        payload_chunks = self._process_payload(data)
        
        success = True
        for chunk in payload_chunks:
            # Construct the final envelope for the relay
            envelope = {
                "id": message_id,
                "timestamp": timestamp,
                "sender": sender,
                "action": action, # Action remains visible for routing
                "payload_chunk": chunk # The actual data is inside here
            }
            
            # If multiple chunks, we might want unique filenames or same ID?
            # Usually relay expects unique filenames.
            # We append chunk index to filename to avoid overwrite.
            chunk_idx = chunk['chunk_index']
            
            try:
                self._write_to_disk(message_id, chunk_idx, envelope)
                logger.info(f"Message {message_id} chunk {chunk_idx} written. Action: {action}")
            except Exception as e:
                logger.error(f"Failed to write message {message_id} chunk {chunk_idx}: {e}")
                success = False
        
        return success

    def _write_to_disk(self, message_id: str, chunk_index: int, payload: dict):
        """Writes the payload to a JSON file in the outbox directory."""
        filename = f"{int(payload['timestamp'])}_{message_id}_{chunk_index}.json"
        file_path = os.path.join(self.outbox_path, filename)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    # Test execution
    dummy_config = {
        "relay": {"chunk_size": 10},
        "assistant": {"auto_chunk_payloads": True, "auto_base64": True}
    }
    handler = OutboxHandler(outbox_path="./test_outbox_norm", config=dummy_config)
    handler.send_message("test_action", {"long_data": "This is a very long string that should be chunked"})
