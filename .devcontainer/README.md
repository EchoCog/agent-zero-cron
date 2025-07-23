# Agent Zero Development Container

This directory contains the configuration for GitHub Codespaces and VS Code development containers.

## What's Included

- **Python 3.12** development environment
- **Docker-in-Docker** support for running Agent Zero containers
- **Node.js LTS** for any frontend development needs
- **VS Code extensions** optimized for Python development
- **Playwright** for browser automation support
- **All system dependencies** required by Agent Zero

## Quick Start

### Using GitHub Codespaces

1. Click the "Code" button on the repository
2. Select "Codespaces" tab
3. Click "Create codespace on main"
4. Wait for the environment to build (first time may take 5-10 minutes)
5. Once ready, edit the `.env` file with your API keys
6. Run `python run_ui.py` to start the web interface

### Using VS Code Dev Containers

1. Install the "Dev Containers" extension in VS Code
2. Open the repository in VS Code
3. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
4. Type "Dev Containers: Reopen in Container"
5. Wait for the container to build
6. Edit the `.env` file with your API keys
7. Start developing!

## Port Forwarding

The following ports are automatically forwarded:

- **50001**: Agent Zero Web UI (primary interface)
- **50080**: Docker container port
- **80**: HTTP server
- **22**: SSH (if needed)

## Environment Setup

After the container starts, the setup script automatically:

1. Creates a `.env` file from `example.env` if it doesn't exist
2. Installs Python dependencies from `requirements.txt`
3. Sets up Playwright browsers
4. Creates necessary directories (`logs`, `memory`, `tmp`)

## Development Workflow

1. **Web UI Development**: Run `python run_ui.py` and access at `http://localhost:50001`
2. **CLI Development**: Run `python run_cli.py` for command-line interface
3. **Debugging**: Use the pre-configured VS Code debugger (F5 key)
4. **Docker Testing**: Use `docker-compose` commands to test containerized versions

## Customization

- Modify `.devcontainer/devcontainer.json` to change VS Code settings or extensions
- Update `.devcontainer/Dockerfile` to add system packages
- Edit `.devcontainer/setup.sh` to customize the post-creation setup

## Troubleshooting

### Container won't start
- Check that Docker is available and running
- Verify the devcontainer.json syntax with `python -m json.tool .devcontainer/devcontainer.json`

### Missing dependencies
- The setup script should handle most dependencies
- For additional system packages, update the Dockerfile
- For Python packages, update requirements.txt

### Port conflicts
- Ensure ports 50001 and 50080 are not in use locally
- Modify the port forwarding in devcontainer.json if needed

## Files

- `devcontainer.json`: Main configuration file
- `Dockerfile`: Custom container image with Agent Zero dependencies
- `setup.sh`: Post-creation setup script
- `README.md`: This documentation

## Performance Tips

- The first build may take 5-10 minutes as it installs all dependencies
- Subsequent starts should be much faster
- Consider using GitHub Codespaces prebuilds for even faster startup times