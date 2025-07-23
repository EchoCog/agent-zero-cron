# Use Python 3.12 base image with development tools
FROM mcr.microsoft.com/devcontainers/python:3.12-bookworm

# Install system dependencies that Agent Zero requires
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    # Core system packages
    locales \
    tzdata \
    curl \
    wget \
    git \
    vim \
    nano \
    # For browser automation (playwright)
    libnss3 \
    libatk-bridge2.0-0 \
    libdrm2 \
    libxkbcommon0 \
    libgtk-3-0 \
    libgbm1 \
    libasound2 \
    # For PDF processing
    poppler-utils \
    # For image processing
    libmagic1 \
    # For development
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set locale and timezone (matching the main Dockerfile)
RUN sed -i -e 's/# \(en_US\.UTF-8 .*\)/\1/' /etc/locale.gen && \
    dpkg-reconfigure --frontend=noninteractive locales && \
    update-locale LANG=en_US.UTF-8 LANGUAGE=en_US:en LC_ALL=en_US.UTF-8
RUN ln -sf /usr/share/zoneinfo/UTC /etc/localtime
RUN echo "UTC" > /etc/timezone
RUN dpkg-reconfigure -f noninteractive tzdata

ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US:en
ENV LC_ALL=en_US.UTF-8
ENV TZ=UTC

# Set environment variables for development
ENV TOKENIZERS_PARALLELISM=true
ENV PYDEVD_DISABLE_FILE_VALIDATION=1

# Create workspace directory
WORKDIR /workspace

# Install Node.js LTS for any frontend tooling
RUN curl -fsSL https://deb.nodesource.com/setup_lts.x | bash - && \
    apt-get install -y nodejs

# Switch back to vscode user
USER vscode