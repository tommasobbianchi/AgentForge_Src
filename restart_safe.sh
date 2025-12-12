#!/bin/bash

# Kill stale processes
pkill -f agentforge_relay.app
pkill -f supervisor_core
pkill -f executor_agent.py
pkill -f planner_agent.py

# Start Shadow Relay
cd ~
export PYTHONPATH=/home/tommaso/projects/AF_patch:~:/opt:$PYTHONPATH
nohup /opt/agentforge_relay/venv/bin/python3 -u -m agentforge_relay.app > ~/relay.log 2>&1 &
echo "Custom Relay started (PID $!)"

# Start Supervisor
cd /opt/agentforge
nohup /opt/agentforge/venv/bin/python3 -u /opt/agentforge/supervisor_core/supervisor_loop.py > ~/supervisor.log 2>&1 &
echo "Supervisor started (PID $!)"

# Start Executor
cd /home/tommaso/projects/AgentForge_Src/Agentforge_MD
# Force restart of executor with unbuffered output
nohup /opt/agentforge/venv/bin/python3 -u executor_agent.py > ~/executor.log 2>&1 &
echo "Executor started (PID $!)"

# Start Planner
cd /opt/agentforge
nohup /opt/agentforge/venv/bin/python3 -u planner_agent.py > ~/planner.log 2>&1 &
echo "Planner started (PID $!)"

# Start Web Interface / Status Server
cd /home/tommaso/projects/AgentForge_Src
nohup python3 Agentforge_MD/web_interface/server.py > ~/web_interface.log 2>&1 &
echo "Web Interface started (PID $!)"

echo "All services started."
