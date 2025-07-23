#!/bin/bash

#
# Agent Zero Guix Deployment Test
# Basic tests to verify Guix deployment configuration
#

set -e

echo "Running Agent Zero Guix deployment tests..."

# Test 1: Check if required files exist
echo "✓ Checking required files..."
required_files=(
    "guix/Dockerfile"
    "guix/manifest.scm"
    "guix/channels.scm"
    "guix/docker-compose.yml"
    "guix/scripts/build.sh"
    "guix/scripts/entrypoint.sh"
    "guix/README.md"
)

for file in "${required_files[@]}"; do
    if [[ ! -f "$file" ]]; then
        echo "✗ Missing required file: $file"
        exit 1
    fi
done

# Test 2: Check script permissions
echo "✓ Checking script permissions..."
if [[ ! -x "guix/scripts/build.sh" ]]; then
    echo "✗ build.sh is not executable"
    exit 1
fi

if [[ ! -x "guix/scripts/entrypoint.sh" ]]; then
    echo "✗ entrypoint.sh is not executable"
    exit 1
fi

# Test 3: Validate Guix manifest syntax (basic check)
echo "✓ Validating Guix manifest syntax..."
if ! grep -q "packages->manifest" guix/manifest.scm; then
    echo "✗ Invalid manifest.scm structure"
    exit 1
fi

# Test 4: Validate channels syntax
echo "✓ Validating Guix channels syntax..."
if ! grep -q "channel" guix/channels.scm; then
    echo "✗ Invalid channels.scm structure"
    exit 1
fi

# Test 5: Check Dockerfile syntax
echo "✓ Validating Dockerfile..."
if ! grep -q "FROM metacall/guix" guix/Dockerfile; then
    echo "✗ Dockerfile does not use metacall/guix base"
    exit 1
fi

# Test 6: Validate docker-compose
echo "✓ Validating docker-compose.yml..."
if ! grep -q "agent-zero-guix" guix/docker-compose.yml; then
    echo "✗ Invalid docker-compose.yml structure"
    exit 1
fi

# Test 7: Check build script help
echo "✓ Testing build script help..."
if ! guix/scripts/build.sh --help | grep -q "Agent Zero Guix Build Script"; then
    echo "✗ Build script help not working"
    exit 1
fi

echo ""
echo "🎉 All tests passed! Guix deployment configuration is valid."
echo ""
echo "Next steps:"
echo "1. Run: bash guix/scripts/build.sh"
echo "2. Or: cd guix && docker-compose up"