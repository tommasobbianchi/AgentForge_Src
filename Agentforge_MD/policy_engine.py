
import logging

logger = logging.getLogger("PolicyEngine")

class PolicyEngine:
    def __init__(self, config=None):
        self.config = config or {}
        # Default allowed actions if not in config
        self.allowed_actions = self.config.get("allowed_actions", [
            "analyze_project",
            "run_diagnostics",
            "plan_next_steps",
            "execute_agent"
        ])

    def validate(self, action: str, data: dict) -> bool:
        """
        Validates an action and its data.
        """
        if action not in self.allowed_actions:
            logger.warning(f"Policy Rejection: Action '{action}' is not allowed.")
            return False
        
        # Further validation could go here
        return True

    def validate_agent(self, agent_name: str) -> bool:
        """
        Validates if an agent is authorized to run.
        """
        # Minimal policy: all agents are valid for now
        # Could check against a whitelist
        return True

    def validate_project(self, project_path: str) -> bool:
        """
        Validates operations on a specific project path.
        """
        # Minimal policy: True
        return True
