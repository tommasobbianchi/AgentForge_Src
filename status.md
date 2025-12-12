# AgentForge Status

**Current Status**: `OPERATIONAL`
**Role**: Hub / Server
**Version**: 0.2.0 (With Web Interface)

## Components
- **Relay**: Active (Port 5101)
- **Web Interface**: Active (Port 5000)
  - `/api/status`: Serves Repository Manifest for spokes.
  - `/api/report`: Receives benchmark reports from spokes.
  - `/api/dashboard`: Displays spoke status.
- **Agents**: Supervisor, Executor, Planner (Managed via `restart_safe.sh`)

## Recent Changes
- Implemented **Propagation Verification System** (Benchmark/Report loop).
- Exposed **Repository Manifest** in `/api/status` for auto-sync.
- Merged `Agentforge_MD` submodule into main repo structure.

