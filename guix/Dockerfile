# syntax = docker/dockerfile:1.1-experimental

#
#	Agent Zero Guix Deployment
#	Docker image using MetaCall Guix for standardized deployment
#
#	Based on MetaCall Guix: https://github.com/metacall/guix
#

FROM metacall/guix:latest AS agent-zero-guix

# Image descriptor
LABEL maintainer="Agent Zero Project" \
	description="Agent Zero with Guix-based deployment" \
	version="0.1"

# Build arguments
ARG BRANCH=main
ARG CACHE_DATE=none

# Environment variables
ENV BRANCH=$BRANCH
ENV GUIX_PROFILE="/root/.config/guix/current"
ENV GUIX_LOCPATH="/root/.guix-profile/lib/locale/"
ENV LANG="en_US.UTF-8"
ENV SSL_CERT_DIR="/root/.guix-profile/etc/ssl/certs"
ENV SSL_CERT_FILE="/root/.guix-profile/etc/ssl/certs/ca-certificates.crt"
ENV GIT_SSL_FILE="/root/.guix-profile/etc/ssl/certs/ca-certificates.crt"
ENV GIT_SSL_CAINFO="/root/.guix-profile/etc/ssl/certs/ca-certificates.crt"
ENV CURL_CA_BUNDLE="/root/.guix-profile/etc/ssl/certs/ca-certificates.crt"

# Copy Guix configuration files
COPY guix/manifest.scm /tmp/manifest.scm
COPY guix/channels.scm /root/.config/guix/channels.scm

# Copy Guix deployment scripts
COPY guix/scripts/ /guix-scripts/

# Install Agent Zero dependencies using Guix
RUN --security=insecure sh -c '/entry-point.sh guix pull' \
	&& sh -c '/entry-point.sh guix package -m /tmp/manifest.scm' \
	&& sh -c '/entry-point.sh guix gc --optimize'

# Clone Agent Zero repository
RUN --security=insecure sh -c '/entry-point.sh git clone -b $BRANCH https://github.com/frdel/agent-zero /a0'

# Install Python dependencies using pip within Guix environment
RUN --security=insecure sh -c '/entry-point.sh bash -c "cd /a0 && python -m pip install --upgrade pip && python -m pip install -r requirements.txt"'

# Copy additional configuration files
COPY guix/config/ /a0-config/

# Set up runtime environment
RUN chmod +x /guix-scripts/*.sh

# Expose ports
EXPOSE 22 80

# Set working directory
WORKDIR /a0

# Use Guix environment as entry point
ENTRYPOINT ["/guix-scripts/entrypoint.sh"]
CMD ["run"]