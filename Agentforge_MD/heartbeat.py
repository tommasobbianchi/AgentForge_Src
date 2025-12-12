
import time

class HeartbeatHandler:
    def __init__(self):
        pass

    def run(self, state, data):
        # We accept state but don't strictly need it for a simple heartbeat
        return {
            "time": time.time(),
            "alive": True,
            "status": "ok"
        }
