# Agent Zero Web UI Documentation

## Overview
Agent Zero Web UI provides a browser-based interface for interacting with the Agent Zero AI system.

## Quick Start
```bash
python3 run_ui.py
```

## Access Points
- **Main UI**: https://50001-echocog-agentzerocron-irwg4lyaxj1.ws-eu120.gitpod.io
- **Port**: 50001
- **Status**: Web UI available at the above URL

## Features
- Chat interface with Agent Zero
- File upload and processing
- Knowledge base management
- Task scheduling and monitoring
- Real-time status updates

## Dependencies
All dependencies are now pre-installed in the container:
- Flask web framework
- LangChain AI integrations
- GitPython for version control
- FAISS for vector search
- Whisper for speech recognition
- And many more...

## Troubleshooting
If you encounter issues:
1. Check that all dependencies are installed: `./install_dependencies.sh`
2. Verify the container is running: `docker ps`
3. Check logs for errors: `tail -f logs/agent-zero.log`

## Session Management
- Current branch: `cursor/start-agent-zero-web-ui-ca50`
- Dependencies: ✅ Fixed and containerized
- Status: Ready for development and testing

---
*Last updated: August 4, 2025*