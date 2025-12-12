
#!/bin/bash
# Kill existing processes (ignore errors)
pkill -f python3 || true
sleep 2

# Start Shadow Relay (Patched)
cd ~
export PYTHONPATH=~:/opt:$PYTHONPATH
nohup /opt/agentforge_relay/venv/bin/python3 -m agentforge_relay.app > ~/relay.log 2>&1 &
echo "Custom Relay started (PID $!)"

# Start Supervisor
cd /opt/agentforge
nohup /opt/agentforge/venv/bin/python3 -m supervisor_core.supervisor_loop > ~/supervisor.log 2>&1 &
echo "Supervisor started (PID $!)"

# Start Executor
cd /opt/agentforge
nohup /opt/agentforge/venv/bin/python3 executor_agent.py > ~/executor.log 2>&1 &
echo "Executor started (PID $!)"

# Start Planner
cd /opt/agentforge
nohup /opt/agentforge/venv/bin/python3 planner_agent.py > ~/planner.log 2>&1 &
echo "Planner started (PID $!)"

echo "All services started."
