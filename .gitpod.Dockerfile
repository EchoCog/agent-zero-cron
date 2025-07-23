# Gitpod Dockerfile for Agent Zero
# Based on gitpod/workspace-python-3.10 with Guix integration

FROM gitpod/workspace-python-3.10:2025-07-23-06-50-33

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
    && rm -rf /var/lib/apt/lists/*

# Install GNU Guix package manager
RUN cd /tmp && \
    wget https://git.savannah.gnu.org/cgit/guix.git/plain/etc/guix-install.sh && \
    chmod +x guix-install.sh && \
    echo "Installing Guix..." && \
    ./guix-install.sh || true

# Set up Guix environment variables
ENV GUIX_PROFILE="/root/.config/guix/current"
ENV GUIX_LOCPATH="/root/.guix-profile/lib/locale/"
ENV PATH="/root/.config/guix/current/bin:/root/.guix-profile/bin:$PATH"
ENV LANG="en_US.UTF-8"
ENV SSL_CERT_DIR="/root/.guix-profile/etc/ssl/certs"
ENV SSL_CERT_FILE="/root/.guix-profile/etc/ssl/certs/ca-certificates.crt"
ENV GIT_SSL_FILE="/root/.guix-profile/etc/ssl/certs/ca-certificates.crt"
ENV GIT_SSL_CAINFO="/root/.guix-profile/etc/ssl/certs/ca-certificates.crt"
ENV CURL_CA_BUNDLE="/root/.guix-profile/etc/ssl/certs/ca-certificates.crt"

# Install Docker for Agent Zero's container features
RUN curl -fsSL https://get.docker.com | sh && \
    usermod -aG docker gitpod

# Install Node.js (required for some Agent Zero features)
RUN curl -fsSL https://deb.nodesource.com/setup_lts.x | bash - && \
    apt-get install -y nodejs

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

# Create directories for Agent Zero
RUN mkdir -p /home/gitpod/agent-zero-logs /home/gitpod/agent-zero-memory

# Set working directory
WORKDIR /workspace/agent-zero-cron

# Copy entrypoint script for Gitpod
COPY --chown=gitpod:gitpod .gitpod/setup.sh /home/gitpod/.gitpod/setup.sh
COPY --chown=gitpod:gitpod .gitpod/deploy.sh /home/gitpod/.gitpod/deploy.sh
RUN chmod +x /home/gitpod/.gitpod/*.sh

# Expose ports used by Agent Zero
EXPOSE 50001 50080 80 8080 22

# Default command (will be overridden by Gitpod tasks)
CMD ["bash"]