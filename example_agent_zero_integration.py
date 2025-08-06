#!/usr/bin/env python3
"""
Example: Integrating Daemon Zero with Agent Zero Workflows

This example shows how to:
1. Create scheduled tasks for Agent Zero
2. Set up workflow orchestration
3. Monitor background agent execution
4. Handle task results and failures

This example assumes Agent Zero dependencies are available.
If not, it will demonstrate the integration pattern using mocks.
"""

import asyncio
import json
import os
import sys
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from daemon_zero import DaemonZero


class AgentZeroIntegrationExample:
    """Example integration between Daemon Zero and Agent Zero."""
    
    def __init__(self):
        self.daemon = None
        self.scheduler = None
        self.workflow_manager = None
    
    async def setup(self):
        """Set up the daemon and components."""
        print("🔧 Setting up Daemon Zero for Agent Zero integration...")
        
        # Create daemon instance
        self.daemon = DaemonZero(
            config_file="agent_zero_daemon_config.json",
            pidfile="/tmp/agent_zero_daemon.pid"
        )
        
        # Load configuration with Agent Zero specific settings
        config = self.daemon.load_config()
        
        # Customize configuration for Agent Zero
        config.update({
            "agent": {
                "model_provider": "openai",
                "model_name": "gpt-4",
                "max_context_length": 8000,
                "temperature": 0.1,
                "system_prompt": "You are a helpful AI assistant running as a background agent."
            },
            "scheduler": {
                "enabled": True,
                "tick_interval": 30,  # Check every 30 seconds
                "max_concurrent_tasks": 3
            },
            "workflow": {
                "enabled": True,
                "inngest_enabled": False,  # Enable if Inngest is configured
                "default_timeout": 300
            }
        })
        
        # Save updated configuration
        with open(self.daemon.config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        # Initialize components
        await self.daemon.initialize_components()
        
        self.scheduler = self.daemon.scheduler
        self.workflow_manager = self.daemon.workflow_manager
        
        print("✅ Daemon Zero setup complete")
    
    async def create_sample_tasks(self):
        """Create sample tasks for Agent Zero."""
        print("\n📋 Creating sample Agent Zero tasks...")
        
        # Define sample tasks that Agent Zero could perform
        sample_tasks = [
            {
                "name": "Daily System Health Check",
                "system_prompt": "You are a system administrator AI. Perform a health check.",
                "prompt": "Check system status, disk space, memory usage, and running processes. Provide a summary report.",
                "schedule": {
                    "minute": "0",
                    "hour": "9",
                    "day": "*",
                    "month": "*",
                    "weekday": "*"
                }
            },
            {
                "name": "Weekly Report Generation",
                "system_prompt": "You are a data analyst AI. Generate comprehensive reports.",
                "prompt": "Analyze the past week's data, identify trends, and create a summary report with insights and recommendations.",
                "schedule": {
                    "minute": "0",
                    "hour": "8",
                    "day": "*",
                    "month": "*",
                    "weekday": "1"  # Monday
                }
            },
            {
                "name": "Code Review Assistant",
                "system_prompt": "You are a senior software engineer AI. Review code for quality and best practices.",
                "prompt": "Review recent code commits, check for potential issues, suggest improvements, and ensure coding standards compliance.",
                "schedule": {
                    "minute": "30",
                    "hour": "14",
                    "day": "*",
                    "month": "*",
                    "weekday": "1-5"  # Weekdays
                }
            },
            {
                "name": "Customer Support Analysis",
                "system_prompt": "You are a customer support AI. Analyze support tickets and responses.",
                "prompt": "Review customer support tickets, identify common issues, analyze response times, and suggest process improvements.",
                "schedule": {
                    "minute": "0",
                    "hour": "17",
                    "day": "*",
                    "month": "*",
                    "weekday": "*"
                }
            }
        ]
        
        # Try to create real tasks if possible, otherwise create mock tasks
        try:
            # Check if we have the real task scheduler
            if hasattr(self.scheduler, '__class__') and "Mock" not in self.scheduler.__class__.__name__:
                print("🎯 Creating real scheduled tasks...")
                
                # Import real task classes
                from python.helpers.task_scheduler import ScheduledTask, TaskSchedule
                
                for task_config in sample_tasks:
                    schedule = TaskSchedule(**task_config["schedule"])
                    
                    task = ScheduledTask.create(
                        name=task_config["name"],
                        system_prompt=task_config["system_prompt"],
                        prompt=task_config["prompt"],
                        schedule=schedule
                    )
                    
                    await self.scheduler.add_task(task)
                    print(f"   ✅ Created: {task_config['name']}")
            
            else:
                print("🎭 Creating mock tasks for demonstration...")
                
                # Create mock tasks
                from minimal_stubs import MockTask
                
                for task_config in sample_tasks:
                    task = MockTask(
                        name=task_config["name"],
                        uuid=f"agent-{task_config['name'].lower().replace(' ', '-')}"
                    )
                    
                    # Store additional info in mock task
                    task.system_prompt = task_config["system_prompt"]
                    task.prompt = task_config["prompt"]
                    task.schedule_info = task_config["schedule"]
                    
                    self.scheduler.add_task(task)
                    print(f"   ✅ Created: {task_config['name']}")
        
        except ImportError:
            print("⚠️ Real task scheduler not available, using mock implementation")
            # Fallback to mock implementation
            from minimal_stubs import MockTask
            
            for task_config in sample_tasks:
                task = MockTask(name=task_config["name"])
                self.scheduler.add_task(task)
                print(f"   ✅ Created mock: {task_config['name']}")
        
        print(f"📊 Total tasks created: {len(self.scheduler.get_tasks())}")
    
    async def create_workflow_example(self):
        """Create an example workflow combining multiple Agent Zero tasks."""
        print("\n🔄 Creating workflow example...")
        
        # Define a workflow that chains multiple agent tasks
        workflow_definition = {
            "name": "Daily Operations Workflow",
            "description": "A complete daily workflow for Agent Zero",
            "steps": [
                {
                    "id": "health-check",
                    "type": "task",
                    "name": "System Health Check",
                    "description": "Check system health before other operations"
                },
                {
                    "id": "delay-1",
                    "type": "delay",
                    "delay_seconds": 60,
                    "description": "Wait 1 minute between steps"
                },
                {
                    "id": "code-review",
                    "type": "task", 
                    "name": "Code Review",
                    "description": "Review any pending code changes",
                    "depends_on": ["health-check"]
                },
                {
                    "id": "conditional-report",
                    "type": "conditional",
                    "condition": {
                        "type": "previous_step_success",
                        "step_id": "code-review"
                    },
                    "if_true": [
                        {
                            "id": "generate-report",
                            "type": "task",
                            "name": "Generate Summary Report",
                            "description": "Create a summary of all completed tasks"
                        }
                    ],
                    "if_false": [
                        {
                            "id": "error-notification",
                            "type": "task",
                            "name": "Send Error Notification",
                            "description": "Notify about workflow failure"
                        }
                    ]
                }
            ]
        }
        
        try:
            # Try to create real workflow
            workflow_id = f"daily-ops-{datetime.now().strftime('%Y%m%d')}"
            
            success = await self.workflow_manager.create_workflow(
                workflow_id=workflow_id,
                workflow_definition=workflow_definition,
                workflow_input={"execution_date": datetime.now().isoformat()}
            )
            
            if success:
                print(f"✅ Created workflow: {workflow_id}")
            else:
                print("⚠️ Workflow creation returned False (may be using mock)")
        
        except Exception as e:
            print(f"⚠️ Workflow creation not available: {e}")
            print("   This is expected when using mock implementations")
    
    async def monitor_execution(self):
        """Monitor task execution and health."""
        print("\n📊 Monitoring daemon execution...")
        
        # Run health check
        health = await self.daemon.health_check()
        print(f"Health Status: {health['status']}")
        print(f"Components: {health['components']}")
        
        # List current tasks
        tasks = self.scheduler.get_tasks()
        print(f"Active Tasks: {len(tasks)}")
        
        for task in tasks:
            print(f"  - {task.name} (State: {task.state})")
            if hasattr(task, 'last_run') and task.last_run:
                print(f"    Last run: {task.last_run}")
            if hasattr(task, 'get_next_run'):
                next_run = task.get_next_run()
                if next_run:
                    print(f"    Next run: {next_run}")
        
        # Run a scheduler tick to process any due tasks
        print("\n⚙️ Running scheduler tick...")
        await self.scheduler.tick()
    
    async def demonstrate_task_execution(self):
        """Demonstrate executing specific tasks."""
        print("\n🚀 Demonstrating task execution...")
        
        tasks = self.scheduler.get_tasks()
        if not tasks:
            print("⚠️ No tasks available for execution")
            return
        
        # Execute first task as an example
        task = tasks[0]
        print(f"🎯 Executing task: {task.name}")
        
        try:
            await self.scheduler.run_task_by_uuid(task.uuid)
            print(f"✅ Task {task.name} completed successfully")
            
            # Show results if available
            if hasattr(task, 'last_result') and task.last_result:
                print(f"Result: {task.last_result}")
        
        except Exception as e:
            print(f"❌ Task execution failed: {e}")
    
    def show_integration_summary(self):
        """Show a summary of the integration."""
        print("\n📋 Integration Summary")
        print("=" * 50)
        
        print("🔧 Components:")
        print(f"   Daemon: {self.daemon.__class__.__name__}")
        print(f"   Scheduler: {self.scheduler.__class__.__name__}")
        print(f"   Workflow Manager: {self.workflow_manager.__class__.__name__}")
        
        print("\n📊 Statistics:")
        tasks = self.scheduler.get_tasks()
        print(f"   Total Tasks: {len(tasks)}")
        
        running_tasks = [t for t in tasks if getattr(t, 'state', 'idle') == 'running']
        print(f"   Running Tasks: {len(running_tasks)}")
        
        print("\n🎯 Key Features Demonstrated:")
        print("   ✅ Daemon lifecycle management")
        print("   ✅ Scheduled task creation")
        print("   ✅ Workflow orchestration")
        print("   ✅ Health monitoring")
        print("   ✅ Task execution")
        print("   ✅ Real/mock component integration")
        
        print("\n🚀 Ready for Production:")
        print("   - Configure real Agent Zero models")
        print("   - Set up Inngest for workflows")
        print("   - Add authentication and security")
        print("   - Deploy as system service")
    
    async def cleanup(self):
        """Clean up resources."""
        print("\n🧹 Cleaning up...")
        if self.daemon:
            self.daemon.cleanup()
        print("✅ Cleanup complete")


async def main():
    """Run the integration example."""
    print("🎯 Agent Zero + Daemon Zero Integration Example")
    print("=" * 60)
    
    example = AgentZeroIntegrationExample()
    
    try:
        # Setup
        await example.setup()
        
        # Create sample tasks
        await example.create_sample_tasks()
        
        # Create workflow example
        await example.create_workflow_example()
        
        # Monitor execution
        await example.monitor_execution()
        
        # Demonstrate task execution
        await example.demonstrate_task_execution()
        
        # Show summary
        example.show_integration_summary()
        
        print("\n🎉 Integration example completed successfully!")
        print("\n📚 Next Steps:")
        print("   1. Install Agent Zero dependencies")
        print("   2. Configure your AI model providers")
        print("   3. Set up authentication and security")
        print("   4. Deploy daemon as a system service")
        print("   5. Monitor and scale as needed")
        
        return 0
    
    except Exception as e:
        print(f"\n💥 Integration example failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    finally:
        await example.cleanup()


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)