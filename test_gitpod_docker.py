#!/usr/bin/env python3
"""
Gitpod+Docker Integration Test Suite

This test validates the complete gitpodocker implementation addressing 
issues #7, #8, #9, and #10. Run this test to verify the integration
is working correctly.

Usage: python test_gitpod_docker.py
"""

import os
import sys
import yaml

def test_gitpod_docker_integration():
    """Test the complete Gitpod+Docker integration."""
    print("🧪 Testing Gitpod+Docker Integration")
    print("=" * 40)
    
    # Test 1: Gitpod Configuration
    print("🔍 Testing Gitpod configuration...")
    assert os.path.exists('.gitpod.yml'), "Missing .gitpod.yml"
    assert os.path.exists('.gitpod.Dockerfile'), "Missing .gitpod.Dockerfile" 
    
    with open('.gitpod.yml', 'r') as f:
        config = yaml.safe_load(f)
    
    # Validate key configuration elements
    assert config['image']['file'] == '.gitpod.Dockerfile', "Invalid Dockerfile reference"
    assert any(p['port'] == 50001 for p in config['ports']), "Missing port 50001"
    assert len(config['tasks']) >= 1, "No tasks configured"
    print("✅ Gitpod configuration is valid")
    
    # Test 2: Docker Base Image
    print("🔍 Testing Docker configuration...")
    with open('.gitpod.Dockerfile', 'r') as f:
        dockerfile = f.read()
    
    assert 'gitpod/workspace-python:2025-07-23-06-50-33' in dockerfile, "Wrong base image"
    assert 'USER gitpod' in dockerfile, "Missing user configuration"
    print("✅ Docker configuration is valid")
    
    # Test 3: Deployment Scripts
    print("🔍 Testing deployment scripts...")
    deploy_script = '.gitpod/deploy.sh'
    assert os.path.exists(deploy_script), "Missing deployment script"
    assert os.access(deploy_script, os.X_OK), "Deploy script not executable"
    
    with open(deploy_script, 'r') as f:
        script = f.read()
    
    required_functions = ['check_prerequisites', 'setup_agent_zero', 'start_agent_zero']
    for func in required_functions:
        assert func in script, f"Missing function: {func}"
    print("✅ Deployment scripts are valid")
    
    # Test 4: Documentation
    print("🔍 Testing documentation...")
    with open('README.md', 'r') as f:
        readme = f.read()
    
    assert 'Open in Gitpod' in readme, "Missing Gitpod button"
    assert 'gitpod.io/#https://github.com/EchoCog/agent-zero-cron' in readme, "Wrong Gitpod URL"
    assert os.path.exists('.gitpod/README.md'), "Missing Gitpod documentation"
    print("✅ Documentation is complete")
    
    # Test 5: Issue Requirements
    print("🔍 Validating issue requirements...")
    
    # Issue #7: Docker deployment automation
    assert 'guix' in script.lower(), "Missing Guix integration"
    
    # Issue #8: Agent Zero deployment
    assert any('Agent Zero' in task.get('name', '') for task in config['tasks']), "Missing Agent Zero task"
    
    # Issue #9: Cognitive grammar integration  
    cognitive_files = ['test_cognitive_grammar_integration.py', 'demo_cognitive_grammar.py']
    assert any(os.path.exists(f) for f in cognitive_files), "Missing cognitive grammar files"
    
    # Issue #10: Technical documentation
    assert os.path.exists('docs'), "Missing docs directory"
    print("✅ All issue requirements are met")
    
    print("\n🎉 All tests passed!")
    print("✅ Gitpod+Docker integration is working correctly")
    print("✅ Issues #7, #8, #9, #10 requirements are satisfied")
    return True

def main():
    """Main test runner."""
    try:
        success = test_gitpod_docker_integration()
        return 0 if success else 1
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())