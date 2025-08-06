#!/usr/bin/env python3
"""
Integration test for Daemon Zero with real Agent Zero components.

This test attempts to use real Agent Zero components when available,
falling back to mocks when they're not.
"""

import asyncio
import json
import os
import sys
import tempfile
from datetime import datetime, timezone

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from daemon_zero import DaemonZero
from minimal_stubs import get_minimal_task_scheduler


async def test_integration():
    """Test integration with available components."""
    print("=== Daemon Zero Integration Test ===\n")
    
    # Create temporary files
    temp_dir = tempfile.mkdtemp()
    config_file = os.path.join(temp_dir, "integration_test_config.json")
    pidfile = os.path.join(temp_dir, "integration_test.pid")
    
    try:
        # Test daemon creation
        print("1. Creating daemon instance...")
        daemon = DaemonZero(config_file=config_file, pidfile=pidfile)
        print("   ✓ Daemon instance created")
        
        # Test configuration loading
        print("\n2. Loading configuration...")
        config = daemon.load_config()
        print(f"   ✓ Configuration loaded: {len(config)} sections")
        
        # Test component initialization
        print("\n3. Initializing components...")
        await daemon.initialize_components()
        
        if hasattr(daemon.scheduler, '__class__'):
            scheduler_type = daemon.scheduler.__class__.__name__
        else:
            scheduler_type = "Unknown"
            
        if hasattr(daemon.workflow_manager, '__class__'):
            workflow_type = daemon.workflow_manager.__class__.__name__
        else:
            workflow_type = "Unknown"
            
        print(f"   ✓ Scheduler: {scheduler_type}")
        print(f"   ✓ Workflow Manager: {workflow_type}")
        
        # Test health check
        print("\n4. Running health check...")
        daemon.start_time = datetime.now(timezone.utc).timestamp()
        health = await daemon.health_check()
        print(f"   ✓ Health status: {health['status']}")
        print(f"   ✓ Components available: {health['components']}")
        
        # Test scheduler operations
        print("\n5. Testing scheduler operations...")
        tasks_before = len(daemon.scheduler.get_tasks())
        print(f"   ✓ Tasks before: {tasks_before}")
        
        # Try to run scheduler tick
        await daemon.scheduler.tick()
        print("   ✓ Scheduler tick completed")
        
        # Test workflow manager status
        print("\n6. Testing workflow manager...")
        if hasattr(daemon.workflow_manager, 'get_status'):
            workflow_status = daemon.workflow_manager.get_status()
            print(f"   ✓ Workflow status: {workflow_status}")
        else:
            print("   ✓ Workflow manager available (basic)")
        
        # Test component integration
        print("\n7. Testing component integration...")
        
        # Check if we're using real or mock components
        real_components = []
        mock_components = []
        
        if "Mock" in scheduler_type:
            mock_components.append("TaskScheduler")
        else:
            real_components.append("TaskScheduler")
            
        if "Mock" in workflow_type:
            mock_components.append("WorkflowManager")
        else:
            real_components.append("WorkflowManager")
        
        if real_components:
            print(f"   ✓ Real components available: {', '.join(real_components)}")
        
        if mock_components:
            print(f"   ✓ Mock components in use: {', '.join(mock_components)}")
        
        # Test configuration values
        print("\n8. Validating configuration...")
        required_sections = ["scheduler", "daemon", "agent", "workflow", "logging"]
        for section in required_sections:
            if section in config:
                print(f"   ✓ {section} section present")
            else:
                print(f"   ✗ {section} section missing")
        
        # Test daemon status methods
        print("\n9. Testing daemon status...")
        status = daemon.get_status()
        print(f"   ✓ Status: {status['status']}")
        
        # Test cleanup
        print("\n10. Testing cleanup...")
        daemon.cleanup()
        print("    ✓ Cleanup completed")
        
        print("\n=== Integration Test Completed Successfully ===")
        
        # Summary
        print(f"\nSummary:")
        print(f"- Configuration file: {config_file}")
        print(f"- PID file: {pidfile}")
        print(f"- Real components: {len(real_components)}")
        print(f"- Mock components: {len(mock_components)}")
        print(f"- Health status: {health['status']}")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Cleanup temporary files
        for file_path in [config_file, pidfile]:
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except:
                    pass


async def test_task_integration():
    """Test task-related integration."""
    print("\n=== Task Integration Test ===\n")
    
    try:
        # Get scheduler
        print("1. Getting task scheduler...")
        scheduler = get_minimal_task_scheduler()
        scheduler_type = scheduler.__class__.__name__
        print(f"   ✓ Scheduler type: {scheduler_type}")
        
        # Test task operations
        print("\n2. Testing task operations...")
        initial_count = len(scheduler.get_tasks())
        print(f"   ✓ Initial task count: {initial_count}")
        
        # Test task addition (mock only)
        if "Mock" in scheduler_type:
            from minimal_stubs import MockTask
            test_task = MockTask("Integration Test Task", "integration-test-123")
            scheduler.add_task(test_task)
            
            new_count = len(scheduler.get_tasks())
            print(f"   ✓ Added task, new count: {new_count}")
            
            # Test task retrieval
            retrieved_task = scheduler.get_task_by_uuid("integration-test-123")
            if retrieved_task:
                print(f"   ✓ Retrieved task: {retrieved_task.name}")
            else:
                print("   ✗ Failed to retrieve task")
                
            # Test task execution
            await scheduler.run_task_by_uuid("integration-test-123")
            print("   ✓ Task execution completed")
            
        else:
            print("   ✓ Real scheduler detected (skipping mock-specific tests)")
        
        # Test scheduler tick
        print("\n3. Testing scheduler tick...")
        await scheduler.tick()
        print("   ✓ Scheduler tick completed")
        
        print("\n=== Task Integration Test Completed ===")
        return True
        
    except Exception as e:
        print(f"\n✗ Task integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_dependency_detection():
    """Test detection of available dependencies."""
    print("\n=== Dependency Detection Test ===\n")
    
    dependencies = {
        "nest_asyncio": "Task scheduler core",
        "langchain_openai": "LangChain OpenAI integration",
        "inngest": "Workflow orchestration",
        "faiss-cpu": "Vector database",
        "flask": "Web interface",
        "crontab": "Cron scheduling"
    }
    
    available = []
    missing = []
    
    for dep, description in dependencies.items():
        try:
            __import__(dep)
            available.append((dep, description))
            print(f"✓ {dep}: {description}")
        except ImportError:
            missing.append((dep, description))
            print(f"✗ {dep}: {description}")
    
    print(f"\nSummary:")
    print(f"- Available dependencies: {len(available)}")
    print(f"- Missing dependencies: {len(missing)}")
    
    if missing:
        print(f"\nMissing dependencies will use fallback implementations:")
        for dep, desc in missing:
            print(f"  - {dep}: {desc}")
    
    return len(available) > 0


async def main():
    """Run all integration tests."""
    print("Daemon Zero Integration Test Suite")
    print("=" * 50)
    
    tests = [
        ("Dependency Detection", test_dependency_detection),
        ("Main Integration", test_integration),
        ("Task Integration", test_task_integration)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\nRunning {test_name}...")
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"Test {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Final summary
    print("\n" + "=" * 50)
    print("Integration Test Results:")
    print("=" * 50)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\nTotal: {len(results)} tests")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 All integration tests passed!")
        return 0
    else:
        print(f"\n❌ {failed} integration test(s) failed")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)