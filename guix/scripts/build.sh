#!/bin/bash

#
# Agent Zero Guix Build Script
# Builds the Agent Zero Docker image using MetaCall Guix
#

set -e

# Default values
IMAGE_NAME="agent-zero-guix"
TAG="latest"
BRANCH="main"
BUILD_ARGS=""

# Function to show help
show_help() {
    echo "Agent Zero Guix Build Script"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -n, --name NAME      Image name (default: agent-zero-guix)"
    echo "  -t, --tag TAG        Image tag (default: latest)"
    echo "  -b, --branch BRANCH  Git branch to use (default: main)"
    echo "  -h, --help          Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                                    # Build with defaults"
    echo "  $0 -n my-agent -t v1.0 -b develop    # Custom build"
    echo ""
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -n|--name)
            IMAGE_NAME="$2"
            shift 2
            ;;
        -t|--tag)
            TAG="$2"
            shift 2
            ;;
        -b|--branch)
            BRANCH="$2"
            shift 2
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Build arguments
BUILD_ARGS="--build-arg BRANCH=$BRANCH --build-arg CACHE_DATE=$(date +%s)"

echo "Building Agent Zero with Guix deployment..."
echo "Image: $IMAGE_NAME:$TAG"
echo "Branch: $BRANCH"
echo ""

# Check if buildx is available and create insecure builder if needed
if docker buildx version > /dev/null 2>&1; then
    echo "Using Docker BuildKit with buildx..."
    
    # Check if insecure builder exists, create if not
    if ! docker buildx ls | grep -q "insecure-builder"; then
        echo "Creating insecure builder for Guix..."
        docker buildx create --use --name insecure-builder --buildkitd-flags '--allow-insecure-entitlement security.insecure'
    else
        echo "Using existing insecure builder..."
        docker buildx use insecure-builder
    fi
    
    # Build with buildx
    docker buildx build \
        -f guix/Dockerfile \
        -t "$IMAGE_NAME:$TAG" \
        --allow security.insecure \
        $BUILD_ARGS \
        .
else
    echo "Warning: Docker buildx not available. Using standard docker build..."
    echo "Note: This may not work properly with Guix due to security restrictions."
    
    # Fallback to regular docker build
    docker build \
        -f guix/Dockerfile \
        -t "$IMAGE_NAME:$TAG" \
        $BUILD_ARGS \
        .
fi

echo ""
echo "Build completed successfully!"
echo "Run with: docker run -p 80:80 $IMAGE_NAME:$TAG"