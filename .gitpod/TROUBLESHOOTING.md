# Gitpod Deployment Troubleshooting

This document provides troubleshooting steps for the Agent Zero Gitpod deployment.

## Common Issues and Solutions

### 1. Workspace Fails to Start

**Symptoms:**
- Gitpod workspace doesn't load
- Build errors during Dockerfile execution
- Tasks fail to complete

**Solutions:**

```bash
# Check Gitpod workspace logs
# Look for errors in the prebuild or startup logs

# Verify Dockerfile builds locally
docker build -f .gitpod.Dockerfile -t agent-zero-gitpod .

# Check YAML syntax
python -c "import yaml; yaml.safe_load(open('.gitpod.yml'))"
```

### 2. Agent Zero Won't Start

**Symptoms:**
- Python dependencies missing
- Module import errors
- Web UI not accessible

**Solutions:**

```bash
# Check deployment logs
cat /tmp/agent-zero-deploy.log

# Manually run deployment
./.gitpod/deploy.sh deploy

# Check Python environment
python --version
pip list | grep -E "(flask|beautifulsoup4|dotenv)"

# Install dependencies manually
pip install -r requirements.txt

# Try starting directly
python run_ui.py
```

### 3. Port Access Issues

**Symptoms:**
- Web UI not accessible via Gitpod URL
- Connection timeouts
- Port forwarding not working

**Solutions:**

```bash
# Check if process is running
ps aux | grep python

# Check port binding
netstat -tlnp | grep 50001

# Verify port configuration in .gitpod.yml
# Make sure ports are set to 'public' visibility

# Try alternative port
python run_ui.py --port 50080
```

### 4. Guix Installation Problems

**Symptoms:**
- Guix commands not found
- Package installation failures
- Permission errors

**Solutions:**

```bash
# Check if Guix is installed
which guix

# Install Guix manually
curl -sSL https://git.savannah.gnu.org/cgit/guix.git/plain/etc/guix-install.sh | bash

# Source Guix profile
source ~/.config/guix/current/etc/profile

# Install packages manually
guix install -m .gitpod/manifest.scm

# Skip Guix and use pip only
AUTO_START=false SKIP_GUIX=true ./.gitpod/deploy.sh deploy
```

### 5. File Permission Issues

**Symptoms:**
- Scripts not executable
- Cannot write to directories
- Access denied errors

**Solutions:**

```bash
# Fix script permissions
chmod +x .gitpod/*.sh

# Check ownership
ls -la .gitpod/

# Fix ownership if needed
sudo chown -R gitpod:gitpod .gitpod/

# Check workspace permissions
ls -la /workspace/
```

## Environment Variables for Debugging

Set these environment variables to control deployment behavior:

```bash
# Skip automatic startup
export AUTO_START=false

# Enable verbose logging
export DEBUG=true

# Skip Guix installation
export SKIP_GUIX=true

# Use alternative port
export AGENT_ZERO_PORT=50080

# Force Gitpod mode
export IN_GITPOD=true

# Skip Python dependency installation
export SKIP_PIP=true
```

## Manual Deployment Steps

If automatic deployment fails, try these manual steps:

```bash
# 1. Install Python dependencies
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# 2. Create environment file
cp example.env .env

# 3. Setup directories
mkdir -p logs memory tmp

# 4. Run preload (optional)
python preload.py --dockerized=true

# 5. Start Agent Zero
python run_ui.py
```

## Gitpod-Specific Commands

```bash
# Open a new terminal
gp tasks list

# Check port status
gp ports list

# Get workspace URL
echo $GITPOD_WORKSPACE_URL

# Check environment variables
env | grep GITPOD

# Open web UI URL
echo "https://50001-$GITPOD_WORKSPACE_ID.$GITPOD_WORKSPACE_CLUSTER_HOST"
```

## Log Files and Debugging

Important log files:

```bash
# Deployment logs
cat /tmp/agent-zero-deploy.log

# Agent Zero logs
ls -la logs/

# Python error logs
python run_ui.py 2>&1 | tee debug.log

# System logs
journalctl --user
```

## Performance Optimization

If the workspace is slow:

```bash
# Check resource usage
htop
df -h

# Optimize Guix
guix gc --optimize

# Clear Python cache
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} +

# Use minimal dependency set
pip install --no-deps -r requirements.txt
```

## Getting Help

1. **Check this troubleshooting guide**
2. **Review deployment logs**: `/tmp/agent-zero-deploy.log`
3. **Check .gitpod/README.md** for detailed documentation
4. **Open an issue** with:
   - Gitpod workspace ID
   - Error messages
   - Steps to reproduce
   - Log files

## Quick Recovery Commands

Emergency commands to get Agent Zero running:

```bash
# Nuclear option - restart everything
pkill python
./.gitpod/deploy.sh deploy

# Minimal startup
cd /workspace/agent-zero-cron
python -m pip install flask python-dotenv
cp example.env .env
python run_ui.py

# Use existing Docker image
docker pull frdel/agent-zero-run
docker run -p 50001:80 frdel/agent-zero-run
```