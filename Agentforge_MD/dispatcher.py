
"""
dispatcher.py — Unified Router v3
"""

from supervisor_core.handlers.run_diagnostics import RunDiagnostics
from supervisor_core.handlers.analyze_project import AnalyzeProject
from supervisor_core.handlers.plan_next_steps import PlanNextSteps
from supervisor_core.handlers.execute_agent import ExecuteAgent
from supervisor_core.handlers.unknown_action import UnknownActionHandler
from supervisor_core.handlers.heartbeat import HeartbeatHandler

class Dispatcher:
    def __init__(self):
        self.handlers = {
            "run_diagnostics": RunDiagnostics(),
            "analyze_project": AnalyzeProject(),
            "plan_next_steps": PlanNextSteps(),
            "execute_agent": ExecuteAgent(),
            "heartbeat": HeartbeatHandler()
        }

    def route(self, action, data, state):
        if action in self.handlers:
            return self.handlers[action].run(state, data)

        return UnknownActionHandler().run(action, data)
