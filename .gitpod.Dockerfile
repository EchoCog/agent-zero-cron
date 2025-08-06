# Gitpod Dockerfile for Agent Zero
# Based on gitpod/workspace-python with Agent Zero dependencies

FROM gitpod/workspace-python:2025-07-23-06-50-33

# Switch to root for system installation
USER root

# Install system dependencies required for Agent Zero and Guix
RUN apt-get update && apt-get install -y \
    # Essential build tools
    build-essential \
    curl \
    wget \
    git \
    # Audio/video processing
    ffmpeg \
    # SSH and networking
    openssh-client \
    openssh-server \
    # Certificate management
    ca-certificates \
    # System utilities
    sudo \
    supervisor \
    cron \
    # Required for Guix
    xz-utils \
    gnupg \
    # Additional system dependencies for Python packages
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Docker for Agent Zero's container features
RUN curl -fsSL https://get.docker.com | sh && \
    usermod -aG docker gitpod && \
    # Ensure Docker socket will be available
    mkdir -p /var/run && \
    chmod 755 /var/run

# Install Node.js (required for some Agent Zero features) using apt package
RUN apt-get update && apt-get install -y nodejs npm && rm -rf /var/lib/apt/lists/*

# Install GNU Guix package manager
RUN cd /tmp && \
    wget https://git.savannah.gnu.org/cgit/guix.git/plain/etc/guix-install.sh && \
    chmod +x guix-install.sh && \
    echo "Installing Guix..." && \
    ./guix-install.sh || true

# Set up Guix environment variables only if Guix profile exists
ENV GUIX_PROFILE="/root/.config/guix/current"
ENV GUIX_LOCPATH="/root/.guix-profile/lib/locale/"
ENV PATH="/root/.config/guix/current/bin:/root/.guix-profile/bin:$PATH"
ENV LANG="en_US.UTF-8"
# Only set SSL variables if the certificate file exists
RUN if [ -f "/root/.guix-profile/etc/ssl/certs/ca-certificates.crt" ]; then \
    echo 'export SSL_CERT_DIR="/root/.guix-profile/etc/ssl/certs"' >> /etc/environment && \
    echo 'export SSL_CERT_FILE="/root/.guix-profile/etc/ssl/certs/ca-certificates.crt"' >> /etc/environment && \
    echo 'export GIT_SSL_FILE="/root/.guix-profile/etc/ssl/certs/ca-certificates.crt"' >> /etc/environment && \
    echo 'export GIT_SSL_CAINFO="/root/.guix-profile/etc/ssl/certs/ca-certificates.crt"' >> /etc/environment && \
    echo 'export CURL_CA_BUNDLE="/root/.guix-profile/etc/ssl/certs/ca-certificates.crt"' >> /etc/environment; \
    fi

# Setup workspace permissions
RUN chown -R gitpod:gitpod /workspace

# Switch back to gitpod user
USER gitpod

# Set up Guix for the gitpod user
RUN echo 'export GUIX_PROFILE="$HOME/.config/guix/current"' >> ~/.bashrc && \
    echo 'export PATH="$GUIX_PROFILE/bin:$PATH"' >> ~/.bashrc && \
    echo 'export GUIX_LOCPATH="$HOME/.guix-profile/lib/locale/"' >> ~/.bashrc

# Install Python packages commonly needed
RUN python -m pip install --upgrade pip setuptools wheel

# Install all Python dependencies from requirements.txt
# Copy requirements.txt first for better Docker layer caching
COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt --break-system-packages

# Install additional dependencies discovered during troubleshooting
RUN pip install \
    cryptography \
    nest-asyncio \
    python-crontab \
    --break-system-packages

# Create directories for Agent Zero
RUN mkdir -p /home/gitpod/agent-zero-logs /home/gitpod/agent-zero-memory

# Set working directory
WORKDIR /workspace/agent-zero-cron

# Setup deployment scripts (they will be available in workspace)
RUN mkdir -p /home/gitpod/.gitpod

# Expose ports used by Agent Zero
EXPOSE 50001 50080 80 8080 22

# Default command (will be overridden by Gitpod tasks)
CMD ["bash"]# Dependency fix branch
