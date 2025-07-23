# Agent Zero Guix Configuration

This directory contains configuration files for the Guix deployment.

## Environment Configuration

Copy and modify these files as needed for your deployment:

### Example .env file

```env
# Agent Zero Configuration
BRANCH=main
PORT=80
SSH_PORT=2222
SEARX_PORT=8080

# Guix Configuration  
GUIX_PROFILE=/root/.config/guix/current
LANG=en_US.UTF-8
```

### Custom Manifest

To add custom packages, create a custom manifest file and modify the Dockerfile to use it.

### SearXNG Configuration

If using the SearXNG service, place custom settings in `searxng/` subdirectory.