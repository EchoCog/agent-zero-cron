# Agent Zero Initialization Sequence

This document describes the comprehensive initialization sequence implemented for Agent Zero that coordinates all components in the proper order.

## Overview

The initialization sequence ensures that all Agent Zero components are started in the correct order with proper dependency management, health checks, and graceful fallbacks. It integrates functionality from issues #3, #4, #5, and #6.

## Supported Environments

The initialization sequence automatically detects and adapts to different runtime environments:

- **GitHub Codespaces** (`CODESPACES=true`) - Issue #3 ✓
- **DevContainer** (`REMOTE_CONTAINERS=true` or `/.devcontainer` exists) - Issue #3 ✓
- **Guix Environment** (`GUIX_ENVIRONMENT` set or `/gnu/store` exists) - Issue #4 ✓
- **Docker Container** (`/.dockerenv` or docker in `/proc/1/cgroup`)
- **Bare Metal** (default fallback)

## Initialization Phases

The sequence consists of 10 ordered phases:

### 1. Environment Detection
- Detects runtime environment (devcontainer, codespaces, guix, docker, bare metal)
- Sets up environment-specific configurations
- **Dependencies**: None
- **Required**: Yes

### 2. Runtime Arguments
- Initializes command-line arguments and runtime configuration
- Sets up argument parsing and processing
- **Dependencies**: Environment Detection
- **Required**: Yes

### 3. Environment Variables
- Loads `.env` file and environment variables
- Initializes application settings
- **Dependencies**: Runtime Arguments
- **Required**: Yes

### 4. Core System Setup
- Creates required directories (`logs`, `memory`, `tmp`, `work_dir`)
- Sets up file system structure
- **Dependencies**: Environment Variables
- **Required**: Yes

### 5. Inngest Client (Issue #5)
- Initializes Inngest workflow orchestration system
- Configures event-driven workflows
- **Dependencies**: Core System Setup
- **Required**: No (optional if not configured)

### 6. Agent Kit (Issue #6)
- Initializes Agent Kit for agent-workflow integration
- Links agents with workflow orchestration
- **Dependencies**: Inngest Client
- **Required**: No (optional if Inngest not available)

### 7. Model Configuration
- Configures AI models (chat, utility, embedding, browser)
- Sets up model providers and parameters
- **Dependencies**: Core System Setup
- **Required**: Yes

### 8. Task Scheduler
- Initializes task scheduling and workflow management
- Sets up background job processing
- **Dependencies**: Model Configuration, Agent Kit
- **Required**: Yes

### 9. Optional Components
- Initializes SSH, Docker, and other optional components
- Sets up environment-specific features
- **Dependencies**: Task Scheduler
- **Required**: No

### 10. Health Validation
- Validates that all critical systems are working
- Performs health checks on initialized components
- **Dependencies**: Optional Components
- **Required**: Yes

## Usage

### Basic Usage

```python
from initialize import initialize

# Use the new initialization sequence (default)
config = initialize()
```

### Advanced Usage

```python
from python.helpers.initialization_sequence import (
    get_initialization_sequence, 
    run_full_initialization
)

# Get the initialization sequence instance
sequence = get_initialization_sequence()

# Run full initialization and get data
initialization_data = run_full_initialization()

# Create agent config from initialized system
config = sequence.get_agent_config()
```

### Legacy Usage

```python
from initialize import initialize_legacy

# Use the legacy initialization (for backward compatibility)
config = initialize_legacy()
```

## Environment-Specific Features

### DevContainer/Codespaces (Issue #3)
- Automatically detects container environments
- Configures appropriate networking and permissions
- Sets up development-specific settings

### Guix Deployment (Issue #4)
- Detects Guix package management environment
- Maintains compatibility with Guix builds
- Uses Guix-specific paths and configurations

### Inngest Integration (Issue #5)
- Initializes workflow orchestration when enabled
- Configures event-driven agent behaviors
- Provides workflow management capabilities

### Agent Kit Integration (Issue #6)
- Links agents with workflow systems
- Enables advanced agent coordination
- Provides state management for multi-agent scenarios

## Health Checks

The system performs comprehensive health validation:

- **✓ AI models configured**: Verifies all required models are set up
- **✓ Core system ready**: Ensures directories and basic systems work
- **ℹ️ Inngest workflow orchestration**: Reports Inngest status (enabled/disabled)
- **ℹ️ Agent Kit integration**: Reports Agent Kit status (active/disabled)

## Error Handling

The initialization sequence provides robust error handling:

- **Required Steps**: Failure stops initialization with clear error messages
- **Optional Steps**: Failures are logged but don't stop the process
- **Dependency Failures**: Dependent steps are skipped if requirements fail
- **Graceful Fallbacks**: System continues with reduced functionality when possible

## Configuration

### Environment Variables

```bash
# Inngest Configuration (Issue #5)
INNGEST_EVENT_KEY=your_event_key
INNGEST_SIGNING_KEY=your_signing_key
INNGEST_BASE_URL=https://api.inngest.com

# Environment Detection
CODESPACES=true                    # GitHub Codespaces
REMOTE_CONTAINERS=true             # DevContainer
GUIX_ENVIRONMENT=/gnu/store/...    # Guix environment
```

### Settings File

The initialization sequence uses the existing Agent Zero settings system for configuration. All model, runtime, and feature settings are respected.

## Troubleshooting

### Common Issues

1. **Missing Dependencies**
   - Check that required packages are installed
   - Optional components will be disabled if dependencies are missing

2. **Permission Errors**
   - Ensure write permissions for `logs`, `memory`, `tmp` directories
   - Check container/environment-specific permission requirements

3. **Environment Detection Issues**
   - Check environment variables (`CODESPACES`, `REMOTE_CONTAINERS`, etc.)
   - Verify file system indicators (`.devcontainer`, `/gnu/store`, etc.)

4. **Inngest Configuration**
   - Verify `INNGEST_EVENT_KEY` and `INNGEST_SIGNING_KEY` are set
   - Check network connectivity to Inngest API

### Debug Mode

Set environment variable `DEBUG=true` for verbose initialization logging:

```bash
DEBUG=true python run_ui.py
```

## Testing

Run the comprehensive test suite:

```bash
python test_initialization_sequence.py
```

This tests:
- Environment detection for all supported environments
- All initialization phases and dependencies
- Inngest integration (Issue #5)
- Agent Kit integration (Issue #6)
- Full initialization sequence
- Error handling and fallbacks

## Migration from Legacy System

The new initialization sequence is backward compatible. Existing code will continue to work without changes. To use new features:

1. **No Changes Required**: Existing `initialize()` calls work automatically
2. **New Features**: Use `get_initialization_sequence()` for advanced features
3. **Legacy Mode**: Use `initialize_legacy()` if issues arise

## Related Documentation

- [DevContainer Setup](../docs/installation.md#devcontainer) - Issue #3
- [Guix Deployment](../guix/README.md) - Issue #4  
- [Inngest Integration](../docs/inngest-integration.md) - Issue #5
- [Agent Kit Guide](../docs/inngest_agent_kit.md) - Issue #6