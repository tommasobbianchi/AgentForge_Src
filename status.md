# AgentForge Status

**Current Status**: `OPERATIONAL`
**Role**: Hub / Server
**Version**: 0.2.0 (With Web Interface)

## Components
- **Relay**: Active (Port 5101)
- **Web Interface**: Active (Port 5000, serving `/api/status`)
- **Agents**: Supervisor, Executor, Planner (Managed via `restart_safe.sh`)

## Recent Changes
- Added `web_interface/server.py` to serve the "Junior Developer" manifesto.
- Updated `restart_safe.sh` to launch the web server automatically.
- Initialized Git repository and pushed to `github.com/tommasobbianchi/AgentForge_Src`.
