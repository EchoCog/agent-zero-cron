# Agent Zero Guix Deployment

This directory contains files for deploying Agent Zero using [GNU Guix](https://guix.gnu.org/) via the [MetaCall Guix](https://github.com/metacall/guix) Docker image. This provides a reproducible, standardized deployment method with better dependency management.

## Overview

The Guix deployment offers several advantages over traditional Docker deployments:

- **Reproducible builds**: Exact dependency versions specified in manifest
- **Portable distributions**: Self-contained packages that work across environments  
- **Better dependency management**: Guix handles complex dependency resolution
- **Standardized deployment**: Consistent deployment patterns across environments

## Quick Start

### Prerequisites

- Docker with BuildX support (Docker 19.03+)
- BuildX plugin installed

### Basic Usage

1. **Build the image:**
   ```bash
   # From the project root
   bash guix/scripts/build.sh
   ```

2. **Run with Docker:**
   ```bash
   docker run -p 80:80 agent-zero-guix:latest
   ```

3. **Run with docker-compose:**
   ```bash
   cd guix/
   docker-compose up
   ```

### Advanced Usage

#### Custom Build Options

```bash
# Build with custom settings
bash guix/scripts/build.sh -n my-agent -t v1.0 -b develop

# Build different branch
bash guix/scripts/build.sh --branch feature-branch --tag experimental
```

#### Environment Variables

```bash
# Set branch and port
BRANCH=develop PORT=8080 docker-compose up
```

## Architecture

### File Structure

```
guix/
├── Dockerfile              # Guix-based Docker image
├── docker-compose.yml      # Compose configuration
├── manifest.scm           # Guix package manifest
├── channels.scm           # Guix channels configuration
├── scripts/
│   ├── build.sh           # Build script
│   └── entrypoint.sh      # Container entrypoint
└── config/                # Configuration files
```

### Key Components

- **manifest.scm**: Defines all Agent Zero dependencies using Guix packages
- **channels.scm**: Specifies Guix channels for reproducible builds  
- **Dockerfile**: Multi-stage build using metacall/guix as base
- **entrypoint.sh**: Manages Guix environment and Agent Zero services

## Installation Requirements

### Docker BuildX Setup

The Guix deployment requires Docker BuildX with insecure entitlements:

```bash
# Install buildx (if not already installed)
docker build --platform=local -o . git://github.com/docker/buildx
mkdir -p ~/.docker/cli-plugins/
mv buildx ~/.docker/cli-plugins/docker-buildx

# Create insecure builder (run once)
docker buildx create --use --name insecure-builder \
  --buildkitd-flags '--allow-insecure-entitlement security.insecure'
```

### Why Insecure Builder?

Guix requires the ability to fork processes during package installation, which is normally forbidden during Docker builds. The `--security=insecure` flag allows this behavior in a controlled manner.

## Configuration

### Package Management

Edit `manifest.scm` to add or modify dependencies:

```scheme
;; Add new packages to the manifest
(packages->manifest
 (list
  ;; Existing packages...
  python-new-package
  some-tool))
```

### Channels

Modify `channels.scm` to use different Guix channels or versions:

```scheme
;; Pin to specific Guix commit for reproducibility
(channel
  (name guix)
  (url "https://git.savannah.gnu.org/git/guix.git")
  (commit "abc123..."))
```

## Usage Examples

### Web UI Mode (Default)

```bash
docker run -p 80:80 agent-zero-guix:latest
# or
docker run -p 80:80 agent-zero-guix:latest run
```

### CLI Mode

```bash
docker run -it agent-zero-guix:latest cli
```

### Development Shell

```bash
docker run -it agent-zero-guix:latest shell
```

### With Docker Compose

```bash
# Basic startup
docker-compose up

# With custom environment
BRANCH=develop PORT=8080 docker-compose up

# Background mode
docker-compose up -d
```

## Troubleshooting

### BuildX Issues

If you encounter BuildX errors:

```bash
# Select the insecure builder
docker buildx use insecure-builder

# Verify builder capabilities
docker buildx ls
```

### Guix Package Issues

If packages fail to install:

1. Check if packages exist in Guix: `guix search package-name`
2. Verify channel configurations in `channels.scm`
3. Update to latest Guix: modify channels.scm to use latest commit

### Permission Issues

The container runs as root for Guix compatibility. For production deployments, consider:

1. Using user namespaces
2. Running services as non-root inside container
3. Implementing security policies

## Comparison with Standard Deployment

| Feature | Standard Docker | Guix Deployment |
|---------|----------------|-----------------|
| Reproducibility | Moderate | High |
| Dependency Management | apt/pip | Guix |
| Build Time | Faster | Slower (first build) |
| Package Isolation | Container-level | Package-level |
| Security | Standard | Enhanced |

## Contributing

To improve the Guix deployment:

1. Test with different Guix package versions
2. Add missing dependencies to manifest.scm
3. Optimize build times
4. Enhance security configurations
5. Add integration tests

## Resources

- [GNU Guix Manual](https://guix.gnu.org/manual/)
- [MetaCall Guix](https://github.com/metacall/guix)
- [Docker BuildX Documentation](https://docs.docker.com/buildx/)
- [Guix Packaging Guidelines](https://guix.gnu.org/manual/en/html_node/Packaging-Guidelines.html)