
import json
import os

STATE_PATH = "/opt/agentforge/runtime/state.json"


class SupervisorState:
    def __init__(self):
        self.state = {
            "agents": {},
            "projects": {},
            "last_cycle": None,
        }
        self._load()

    def _load(self):
        if os.path.exists(STATE_PATH):
            try:
                with open(STATE_PATH, "r") as f:
                    self.state = json.load(f)
            except Exception:
                pass

    def save(self):
        try:
            with open(STATE_PATH, "w") as f:
                json.dump(self.state, f, indent=2)
        except Exception as e:
            print("Failed to save SupervisorState:", e)

    def update_agent(self, name, info):
        self.state["agents"][name] = info
        self.save()

    def update_project(self, name, info):
        self.state["projects"][name] = info
        self.save()

    def set_last_cycle(self, cycle_data):
        self.state["last_cycle"] = cycle_data
        self.save()

    @property
    def projects(self):
        return self.state.get("projects", {})
    
    @property
    def agents(self):
        return self.state.get("agents", {})
