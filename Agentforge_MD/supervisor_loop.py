
"""
supervisor_loop.py — Stable Event Loop
"""

import time
import logging
from supervisor_core.supervisor import Supervisor
from supervisor_core.message_bus import MessageBus

# Configure logging if not already done
logger = logging.getLogger("SupervisorLoop")

class SupervisorLoop:
    def __init__(self, interval=2.0):
        self.interval = interval
        self.supervisor = Supervisor()
        self.bus = MessageBus()
        self.cycle_count = 0

    def step(self):
        try:
            # Heartbeat Logic
            self.cycle_count += 1
            if self.cycle_count % 20 == 0:
                self._send_heartbeat()

            messages = self.bus.pull("supervisor")

            for msg in messages:
                sender = msg.get("sender", "unknown")
                payload = msg.get("payload", {})

                action = payload.get("action")
                data = payload.get("data", {})

                logger.info(f"Processing action: {action} from {sender}")
                
                try:
                    result = self.supervisor.process(action, data)
                    status = "ok"
                except Exception as e:
                    logger.error(f"Error processing action {action}: {e}")
                    result = {"error": str(e)}
                    status = "error"

                self.bus.push(sender, {
                    "status": status,
                    "action": action,
                    "result": result
                })
        
        except Exception as e:
            # Global Loop Hardening
            logger.error(f"[SupervisorLoop] Critical Error in step: {e}")

    def _send_heartbeat(self):
        try:
            hb_payload = {
                "event": "heartbeat",
                "cycle": self.cycle_count,
                "timestamp": time.time()
            }
            # Target 'chatgpt' as requested in todo.md
            self.bus.push("chatgpt", hb_payload)
            logger.info(f"Sent heartbeat at cycle {self.cycle_count}")
        except Exception as e:
            logger.error(f"Failed to send heartbeat: {e}")

    def run_forever(self):
        logger.info("Starting Supervisor Loop...")
        while True:
            self.step()
            time.sleep(self.interval)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    loop = SupervisorLoop(interval=2.0)
    loop.run_forever()
