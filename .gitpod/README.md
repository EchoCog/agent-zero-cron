# Agent Zero Gitpod Deployment

This directory contains configuration files for deploying Agent Zero in Gitpod with automated Guix build & deploy processes.

## Overview

The Gitpod deployment provides a one-click solution to run Agent Zero in the cloud using:

- **Base Image**: `gitpod/workspace-python:2025-07-23-06-50-33`
- **Package Manager**: GNU Guix for reproducible builds
- **Automation**: Complete automated setup and deployment
- **Access**: Web UI accessible via Gitpod's port forwarding

## Files

### Core Configuration
- `.gitpod.yml` - Main Gitpod workspace configuration
- `.gitpod.Dockerfile` - Custom Docker image based on Gitpod Python workspace
- `setup.sh` - Environment setup script
- `deploy.sh` - Main deployment automation script

### Guix Integration
- `manifest.scm` - Gitpod-optimized Guix package manifest
- Integration with existing `../guix/` configuration

## Quick Start

1. **Click the button**: [![Open in Gitpod](https://gitpod.io/button/open-in-gitpod.svg)](https://gitpod.io/#https://github.com/EchoCog/agent-zero-cron)

2. **Wait for automatic setup**: Gitpod will automatically:
   - Build the custom Docker environment
   - Install Guix and dependencies
   - Set up the Python environment
   - Run Agent Zero preload
   - Start the web interface

3. **Access Agent Zero**: The web UI will be available on port 50001

## Manual Operations

If you need to run operations manually:

```bash
# Deploy Agent Zero
./.gitpod/deploy.sh deploy

# Start Agent Zero (if not auto-started)
./.gitpod/deploy.sh start

# Check status
./.gitpod/deploy.sh status

# Start web UI directly
python run_ui.py

# Start CLI interface
python run_cli.py
```

## Environment Details

### Ports
- **50001**: Main Agent Zero Web UI
- **50080**: Alternative port
- **80**: HTTP server port  
- **8080**: SearXNG search service (optional)

### Directories
- `/workspace/agent-zero-cron`: Main workspace
- `logs/`: Agent Zero log files
- `memory/`: Agent Zero memory persistence
- `tmp/`: Temporary files

### Environment Variables
- `GITPOD_WORKSPACE_ID`: Gitpod workspace identifier
- `GITPOD_WORKSPACE_URL`: Base workspace URL
- `IN_GITPOD=true`: Set when running in Gitpod
- `AGENT_ZERO_PORT=50001`: Web UI port

## Guix Integration

The deployment integrates with the existing Guix configuration:

1. **Optimized Manifest**: `.gitpod/manifest.scm` contains a minimal package set
2. **Fallback Support**: Falls back gracefully if Guix is not available
3. **Reproducible Builds**: Leverages Guix for dependency management
4. **Compatibility**: Works with existing `guix/` directory structure

## Troubleshooting

### Common Issues

**Environment not starting**:
- Check the Gitpod build logs
- Verify the Dockerfile builds successfully
- Check `.gitpod/deploy.sh` logs

**Web UI not accessible**:
- Ensure port 50001 is properly forwarded
- Check that Agent Zero started successfully
- Verify Gitpod port visibility settings

**Guix issues**:
- The deployment will continue without Guix if installation fails
- Check Guix logs in `/tmp/agent-zero-deploy.log`
- Verify the manifest file is valid

### Debug Commands

```bash
# Check deployment logs
cat /tmp/agent-zero-deploy.log

# Verify Python environment
python --version
pip list

# Check Guix status
guix --version

# Check running processes
ps aux | grep python

# Check port binding
netstat -tlnp | grep 50001
```

## Development

To modify the Gitpod deployment:

1. **Update Configuration**: Edit `.gitpod.yml` for workspace settings
2. **Modify Environment**: Update `.gitpod.Dockerfile` for system packages
3. **Change Automation**: Edit `deploy.sh` for deployment logic
4. **Adjust Packages**: Modify `manifest.scm` for Guix packages

## Comparison with Other Deployments

| Feature | Gitpod | Docker | Guix |
|---------|---------|--------|------|
| Setup Time | Instant | Medium | Slow |
| Accessibility | Web Browser | Local | Local |
| Reproducibility | High | Medium | Highest |
| Customization | Medium | High | Highest |
| Dependencies | Automated | Manual | Automated |

## Support

For issues specific to the Gitpod deployment:

1. Check this README for troubleshooting steps
2. Review logs in `/tmp/agent-zero-deploy.log`
3. Open an issue in the repository with Gitpod-specific details
4. Include your Gitpod workspace ID and error messages