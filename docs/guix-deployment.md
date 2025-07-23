# Guix-based Deployment Guide

This guide explains how to deploy Agent Zero using GNU Guix via the MetaCall Guix Docker image, providing reproducible builds and standardized deployment patterns.

## Overview

The Guix deployment provides several advantages:

- **Reproducible builds**: Every build uses exactly the same dependency versions
- **Better dependency management**: Guix resolves complex dependencies automatically
- **Portable distributions**: Self-contained packages that work across different environments
- **Standardized deployment**: Consistent patterns for CI/CD and production deployments

## Architecture

The Guix deployment uses a multi-stage approach:

1. **Base Stage**: Uses `metacall/guix:latest` as the foundation
2. **Package Installation**: Installs dependencies using Guix manifest
3. **Application Setup**: Clones Agent Zero and installs Python dependencies
4. **Runtime Configuration**: Sets up services and entry points

### Key Components

```
guix/
├── Dockerfile              # Multi-stage Guix-based build
├── manifest.scm           # Guix package manifest (dependencies)
├── channels.scm           # Guix channels configuration
├── docker-compose.yml     # Orchestration for services
├── scripts/
│   ├── build.sh           # Build script with BuildX support
│   ├── entrypoint.sh      # Container runtime management
│   └── test.sh            # Validation tests
└── config/
    └── example.env        # Environment configuration template
```

## Prerequisites

### Docker BuildX

The Guix deployment requires Docker BuildX with insecure entitlements:

```bash
# Install BuildX (if not already available)
docker build --platform=local -o . git://github.com/docker/buildx
mkdir -p ~/.docker/cli-plugins/
mv buildx ~/.docker/cli-plugins/docker-buildx

# Create insecure builder (required for Guix)
docker buildx create --use --name insecure-builder \
  --buildkitd-flags '--allow-insecure-entitlement security.insecure'
```

### Why Insecure Builder?

Guix requires the ability to fork processes during package installation, which Docker normally prohibits during builds. The `--security=insecure` flag allows this in a controlled manner.

## Installation

### Quick Start

```bash
# Clone repository
git clone https://github.com/EchoCog/agent-zero-cron.git
cd agent-zero-cron

# Build Guix image
bash guix/scripts/build.sh

# Run with Docker
docker run -p 80:80 agent-zero-guix:latest

# Or use docker-compose
cd guix/
docker-compose up
```

### Custom Build

```bash
# Build with custom settings
bash guix/scripts/build.sh \
  --name my-agent-zero \
  --tag v1.0 \
  --branch develop

# Run custom build
docker run -p 8080:80 my-agent-zero:v1.0
```

## Configuration

### Environment Variables

Create a `.env` file in the `guix/` directory:

```env
# Agent Zero Configuration
BRANCH=main
PORT=80
SSH_PORT=2222

# Guix Environment
GUIX_PROFILE=/root/.config/guix/current
LANG=en_US.UTF-8
```

### Package Management

Edit `guix/manifest.scm` to modify dependencies:

```scheme
;; Add or remove packages
(packages->manifest
 (list
  ;; Core packages
  python
  node
  git
  
  ;; Add custom packages
  python-custom-package
  some-new-tool))
```

### Channels Configuration

Modify `guix/channels.scm` for different Guix versions:

```scheme
;; Pin to specific commit for reproducibility
(channel
  (name guix)
  (url "https://git.savannah.gnu.org/git/guix.git")
  (commit "abc123..."))  ; Specific commit hash
```

## Usage Examples

### Web UI Mode (Default)

```bash
# Start web interface
docker run -p 80:80 agent-zero-guix:latest

# With custom port
docker run -p 8080:80 agent-zero-guix:latest

# Background mode
docker run -d -p 80:80 agent-zero-guix:latest
```

### CLI Mode

```bash
# Interactive CLI
docker run -it agent-zero-guix:latest cli

# With mounted directory
docker run -it -v $(pwd)/workspace:/workspace agent-zero-guix:latest cli
```

### Development Mode

```bash
# Drop into Guix shell
docker run -it agent-zero-guix:latest shell

# With development branch
docker run -it \
  -e BRANCH=develop \
  agent-zero-guix:latest shell
```

### Docker Compose Deployment

```bash
# Basic deployment
cd guix/
docker-compose up

# With environment customization
BRANCH=develop PORT=8080 docker-compose up

# Production deployment
docker-compose -f docker-compose.yml up -d
```

## CI/CD Integration

### GitHub Actions

The repository includes a GitHub Actions workflow (`.github/workflows/guix-build.yml`) that:

1. Tests the Guix configuration
2. Builds the Docker image using BuildX
3. Runs basic smoke tests
4. Optionally pushes to Docker Hub

### Custom CI/CD

For other CI systems, use this pattern:

```bash
# Install BuildX and create insecure builder
docker buildx create --use --name insecure-builder \
  --buildkitd-flags '--allow-insecure-entitlement security.insecure'

# Test configuration
bash guix/scripts/test.sh

# Build image
bash guix/scripts/build.sh -n $IMAGE_NAME -t $BUILD_TAG

# Test image
docker run --rm $IMAGE_NAME:$BUILD_TAG help
```

## Troubleshooting

### BuildX Issues

**Error**: `granting entitlement security.insecure is not allowed`

**Solution**:
```bash
# Ensure insecure builder is selected
docker buildx use insecure-builder

# Verify builder exists
docker buildx ls | grep insecure-builder
```

### Guix Package Issues

**Error**: Package not found in Guix

**Solution**:
1. Search for available packages: `guix search package-name`
2. Check different package naming conventions
3. Consider using Python pip for packages not in Guix

**Error**: Build fails during Guix operations

**Solution**:
```bash
# Update to latest Guix
# Modify channels.scm to use latest commit
# Or try a known stable commit
```

### Performance Issues

**Issue**: Slow build times

**Solutions**:
- Use Docker layer caching
- Pin Guix to stable commits
- Use a local Guix substitute server
- Build base images separately

### Runtime Issues

**Issue**: Container exits immediately

**Debug**:
```bash
# Check container logs
docker logs <container-id>

# Run in debug mode
docker run -it agent-zero-guix:latest shell

# Test entry point manually
docker run -it agent-zero-guix:latest bash
```

## Comparison with Standard Deployment

| Aspect | Standard Docker | Guix Deployment |
|--------|----------------|-----------------|
| **Reproducibility** | Moderate (base image + packages) | High (exact dependencies) |
| **Build Time** | Fast | Slower initially |
| **Dependency Management** | apt + pip | Guix unified |
| **Caching** | Docker layers | Guix store + Docker layers |
| **Security** | Standard container | Enhanced isolation |
| **Portability** | Good | Excellent |
| **Debugging** | Docker tools | Docker + Guix tools |

## Best Practices

### Development

1. **Pin Dependencies**: Use specific commits in `channels.scm`
2. **Test Locally**: Run `guix/scripts/test.sh` before commits
3. **Layer Optimization**: Order Dockerfile commands by change frequency
4. **Environment Isolation**: Use separate manifests for different environments

### Production

1. **Security**: Review insecure builder requirements
2. **Monitoring**: Include health checks in compose files
3. **Persistence**: Mount volumes for logs and memory
4. **Updates**: Test Guix updates in staging first

### CI/CD

1. **Caching**: Use Docker registry for base images
2. **Testing**: Include smoke tests in pipelines
3. **Security Scanning**: Add container security scans
4. **Rollback**: Keep previous image versions

## Migration from Standard Deployment

### Step-by-Step Migration

1. **Assess Dependencies**: Review current `requirements.txt` and system packages
2. **Create Manifest**: Map dependencies to Guix packages in `manifest.scm`
3. **Test Build**: Use the Guix build locally
4. **Compare Results**: Verify functionality matches standard deployment
5. **Update CI/CD**: Modify pipelines to use Guix builds
6. **Monitor**: Watch for any runtime differences

### Handling Missing Packages

If some dependencies aren't available in Guix:

```dockerfile
# Option 1: Use pip in addition to Guix
RUN --security=insecure sh -c '/entry-point.sh pip install missing-package'

# Option 2: Create custom Guix package
# Add to manifest.scm or create local package definition
```

## Resources

- [GNU Guix Manual](https://guix.gnu.org/manual/)
- [MetaCall Guix Documentation](https://github.com/metacall/guix)
- [Docker BuildX Guide](https://docs.docker.com/buildx/)
- [Guix Cookbook](https://guix.gnu.org/cookbook/)
- [Reproducible Builds](https://reproducible-builds.org/)