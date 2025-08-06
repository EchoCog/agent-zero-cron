# Daemon Zero - Background Agent Daemon for Agent Zero

Daemon Zero provides background processing capabilities for Agent Zero, enabling continuous operation of scheduled tasks, background agents, and workflow orchestration.

## Features

- **Background Task Scheduling**: Run Agent Zero tasks on schedules using cron-like syntax
- **Daemon Process Management**: Full daemon lifecycle management with start/stop/restart controls
- **Task Workflow Orchestration**: Integration with Inngest for complex workflow patterns
- **Health Monitoring**: Built-in health checks and status monitoring
- **Command Line Interface**: Comprehensive CLI for daemon and task management
- **Configuration Management**: Flexible JSON-based configuration system
- **Graceful Shutdown**: Proper signal handling and cleanup
- **Auto-restart**: Configurable automatic restart on failures
- **Logging**: Structured logging with rotation and multiple output formats

## Quick Start

### 1. Start the Daemon

```bash
# Start daemon in background
./daemon_control.sh start

# Or start in foreground for development
./daemon_control.sh start --foreground
```

### 2. Check Status

```bash
# Check if daemon is running
./daemon_control.sh status

# Detailed health check
./daemon_control.sh cli daemon health
```

### 3. Manage Tasks

```bash
# List all tasks
./daemon_control.sh cli tasks list

# Add a new task
./daemon_control.sh cli tasks add "Daily Backup Task"

# Run scheduler tick manually
./daemon_control.sh cli scheduler tick
```

### 4. View Logs

```bash
# Show recent logs
./daemon_control.sh logs

# Follow logs in real-time
./daemon_control.sh logs follow
```

## Installation

### Prerequisites

- Python 3.8 or higher
- Agent Zero repository
- Optional: systemd for system service installation

### Basic Installation

1. Clone this repository or ensure you have the daemon files
2. Make the control script executable:
   ```bash
   chmod +x daemon_control.sh
   ```
3. Install dependencies (if available):
   ```bash
   pip install -r requirements.txt
   ```

### System Service Installation

To install as a systemd service (requires root):

```bash
sudo ./daemon_control.sh install-service
sudo systemctl start daemon-zero
sudo systemctl enable daemon-zero
```

## Configuration

The daemon uses a JSON configuration file (`daemon_config.json`) with the following structure:

```json
{
  "scheduler": {
    "enabled": true,
    "tick_interval": 60,
    "max_concurrent_tasks": 5
  },
  "workflow": {
    "enabled": true,
    "inngest_enabled": false
  },
  "agent": {
    "model_provider": "openai",
    "model_name": "gpt-4",
    "max_context_length": 8000
  },
  "daemon": {
    "auto_restart": true,
    "health_check_interval": 300,
    "max_memory_mb": 2048
  },
  "logging": {
    "level": "INFO",
    "max_files": 10,
    "max_size_mb": 100
  }
}
```

### Configuration Options

#### Scheduler Settings
- `enabled`: Enable/disable task scheduler
- `tick_interval`: How often to check for due tasks (seconds)
- `max_concurrent_tasks`: Maximum number of tasks to run simultaneously

#### Workflow Settings
- `enabled`: Enable/disable workflow orchestration
- `inngest_enabled`: Enable/disable Inngest integration

#### Agent Settings
- `model_provider`: AI model provider (openai, anthropic, etc.)
- `model_name`: Specific model to use
- `max_context_length`: Maximum context window size

#### Daemon Settings
- `auto_restart`: Automatically restart on failures
- `health_check_interval`: How often to perform health checks (seconds)
- `max_memory_mb`: Memory limit for health monitoring

#### Logging Settings
- `level`: Log level (DEBUG, INFO, WARNING, ERROR)
- `max_files`: Maximum number of log files to keep
- `max_size_mb`: Maximum size per log file

## Command Line Interface

### Daemon Management

```bash
# Start daemon
daemon_cli.py daemon start [--foreground]

# Stop daemon
daemon_cli.py daemon stop

# Restart daemon
daemon_cli.py daemon restart

# Check status
daemon_cli.py daemon status [--json]

# Health check
daemon_cli.py daemon health
```

### Task Management

```bash
# List all tasks
daemon_cli.py tasks list

# Add a new task
daemon_cli.py tasks add "Task Name" [--uuid UUID]

# Remove a task
daemon_cli.py tasks remove UUID

# Run a specific task
daemon_cli.py tasks run UUID
```

### Scheduler Management

```bash
# Manually trigger scheduler tick
daemon_cli.py scheduler tick
```

### Configuration Management

```bash
# Show current configuration
daemon_cli.py config show
```

## Control Script

The `daemon_control.sh` script provides a convenient wrapper for common operations:

```bash
# Daemon lifecycle
./daemon_control.sh start
./daemon_control.sh stop
./daemon_control.sh restart
./daemon_control.sh status

# Monitoring
./daemon_control.sh logs [lines]
./daemon_control.sh logs follow

# CLI access
./daemon_control.sh cli [command] [args...]

# System service
sudo ./daemon_control.sh install-service
```

## Architecture

### Components

1. **DaemonZero**: Main daemon class handling process lifecycle
2. **TaskScheduler**: Manages scheduled and ad-hoc tasks
3. **WorkflowManager**: Handles complex workflow orchestration
4. **CLI Interface**: Command-line interface for management
5. **Health Monitor**: Continuous health and performance monitoring

### Integration with Agent Zero

When full Agent Zero dependencies are available, Daemon Zero integrates with:

- **TaskScheduler**: Real task scheduling with persistence
- **Inngest Workflows**: Event-driven workflow orchestration
- **Agent Context**: Full agent execution environment
- **Vector Database**: Memory and knowledge integration
- **Model Providers**: All supported AI model providers

When dependencies are missing, Daemon Zero falls back to mock implementations that provide basic functionality for testing and development.

## Development

### Running Tests

```bash
python test_daemon_zero.py
```

### Mock Mode

When Agent Zero dependencies are not available, the daemon runs in "mock mode" with simplified implementations. This allows development and testing without the full dependency stack.

### Adding New Features

1. **Task Types**: Extend the task scheduler with new task types
2. **Workflow Steps**: Add new workflow step types to the workflow manager
3. **Health Checks**: Add custom health check functions
4. **CLI Commands**: Extend the CLI with new commands

## Troubleshooting

### Common Issues

1. **Daemon won't start**
   - Check log file: `/tmp/daemon_zero.log`
   - Verify configuration file is valid JSON
   - Ensure Python dependencies are installed

2. **Tasks not executing**
   - Check scheduler is enabled in configuration
   - Verify task schedules are correctly formatted
   - Check daemon logs for error messages

3. **High memory usage**
   - Adjust `max_memory_mb` in configuration
   - Check for memory leaks in custom tasks
   - Monitor health check warnings

4. **Permission issues**
   - Ensure daemon user has write access to log directory
   - Check PID file location permissions
   - Verify configuration file is readable

### Log Analysis

Daemon logs are structured with timestamps and log levels:

```
2025-08-04 10:55:28,797 - daemon_zero - INFO - Daemon Zero started successfully
2025-08-04 10:55:28,797 - daemon_zero - INFO - Starting main daemon loop
2025-08-04 10:55:28,797 - daemon_zero - INFO - Health check: healthy
```

Key log messages to watch for:
- `Daemon Zero started successfully`: Successful startup
- `Health check: healthy`: Regular health status
- `Mock scheduler initialized`: Running in mock mode
- `Task completed`: Successful task execution
- `ERROR`: Any error conditions

## Performance Optimization

### Memory Management
- Monitor memory usage via health checks
- Set appropriate `max_memory_mb` limits
- Use task context cleanup

### Task Scheduling
- Optimize `tick_interval` for your workload
- Limit `max_concurrent_tasks` based on resources
- Use planned tasks for complex scheduling

### Workflow Efficiency
- Design workflows to minimize state transitions
- Use conditional steps to avoid unnecessary processing
- Implement proper error handling

## Security Considerations

- Run daemon with minimal privileges
- Secure configuration files (contain API keys)
- Monitor log files for sensitive information
- Use systemd security features when available
- Implement task validation and sanitization

## License

This project is part of Agent Zero and follows the same licensing terms.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review daemon logs
3. Open an issue on the Agent Zero repository
4. Join the Agent Zero community discussions