#!/usr/bin/env python3
"""
Test script for roadmap_parser.py
"""

import unittest
import tempfile
import os
from roadmap_parser import RoadmapParser, Task

class TestRoadmapParser(unittest.TestCase):
    
    def setUp(self):
        """Create a temporary roadmap file for testing."""
        self.test_roadmap_content = """# Agent Zero Development Roadmap

## Development Phases

### Phase 1: Stability & Performance (Q1 2024) 🔥 **HIGH PRIORITY**

#### 1.1 Build & Performance Issues
- [ ] **Fix build blocking errors** identified in TODO.md
  - Resolve module import issues
  - Fix dependency conflicts
  - Optimize build process
- [x] **Completed task** that should be ignored
  - This is already done
- [ ] **Performance optimization**
  - Profile memory usage and optimize
  - Improve response times

### Phase 2: Feature Enhancement (Q2 2024) 🚀 **MEDIUM PRIORITY**

#### 2.1 Advanced Agent Capabilities
- [ ] **Enhanced cognitive abilities**
  - Improved reasoning and planning
  - Better context awareness
"""
        
        # Create temporary file
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.md')
        self.temp_file.write(self.test_roadmap_content)
        self.temp_file.close()
        
    def tearDown(self):
        """Clean up temporary file."""
        os.unlink(self.temp_file.name)
    
    def test_parse_roadmap(self):
        """Test basic roadmap parsing."""
        parser = RoadmapParser(self.temp_file.name)
        tasks = parser.parse()
        
        # Should find 3 tasks (excluding completed one)
        self.assertGreater(len(tasks), 0)
        
        # Check that we got the right number of incomplete tasks
        incomplete_tasks = parser.get_incomplete_tasks()
        self.assertEqual(len(incomplete_tasks), 3)  # 3 incomplete tasks
        
    def test_task_details(self):
        """Test that task details are properly extracted."""
        parser = RoadmapParser(self.temp_file.name)
        tasks = parser.parse()
        incomplete_tasks = parser.get_incomplete_tasks()
        
        # Find the "Fix build blocking errors" task
        build_task = next((t for t in incomplete_tasks if "Fix build blocking errors" in t.title), None)
        self.assertIsNotNone(build_task)
        
        # Check details
        self.assertEqual(build_task.phase, "Stability & Performance")
        self.assertEqual(build_task.priority, "HIGH PRIORITY")
        self.assertEqual(build_task.section, "1.1 Build & Performance Issues")
        self.assertIn("Resolve module import issues", build_task.description)
        self.assertFalse(build_task.is_completed)
        
    def test_priority_filtering(self):
        """Test priority filtering."""
        parser = RoadmapParser(self.temp_file.name)
        tasks = parser.parse()
        high_priority_tasks = parser.get_high_priority_tasks()
        
        # Should have 2 high priority tasks
        self.assertEqual(len(high_priority_tasks), 2)
        
        for task in high_priority_tasks:
            self.assertIn("HIGH", task.priority)
            
    def test_issue_format_conversion(self):
        """Test conversion to GitHub issue format."""
        parser = RoadmapParser(self.temp_file.name)
        tasks = parser.parse()
        incomplete_tasks = parser.get_incomplete_tasks()
        
        if incomplete_tasks:
            task = incomplete_tasks[0]
            issue_format = task.to_issue_format()
            
            self.assertIn("title", issue_format)
            self.assertIn("body", issue_format)  
            self.assertIn("labels", issue_format)
            self.assertIn("roadmap-generated", issue_format["labels"])
            self.assertTrue(any(label.startswith("priority:") for label in issue_format["labels"]))

if __name__ == '__main__':
    unittest.main()