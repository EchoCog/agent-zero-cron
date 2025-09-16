#!/usr/bin/env python3
"""
Parse DEVELOPMENT_ROADMAP.md and extract actionable tasks that can be converted to GitHub issues.
"""

import re
import json
import sys
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

@dataclass
class Task:
    """Represents a single task from the roadmap."""
    title: str
    description: str
    phase: str
    priority: str
    section: str
    is_completed: bool
    line_number: int
    
    def to_issue_format(self) -> Dict:
        """Convert task to GitHub issue format."""
        labels = []
        
        # Add priority label
        if "HIGH PRIORITY" in self.priority:
            labels.append("priority:high")
        elif "MEDIUM PRIORITY" in self.priority:
            labels.append("priority:medium")
        else:
            labels.append("priority:low")
            
        # Add phase label
        labels.append(f"phase:{self.phase.lower().replace(' ', '-')}")
        
        # Add type label
        labels.append("type:enhancement")
        labels.append("roadmap-generated")
        
        body = f"""## Description
{self.description}

## Phase
{self.phase}

## Priority
{self.priority}

## Section
{self.section}

---
*This issue was automatically generated from DEVELOPMENT_ROADMAP.md*
"""
        
        return {
            "title": self.title,
            "body": body,
            "labels": labels
        }

class RoadmapParser:
    """Parse the DEVELOPMENT_ROADMAP.md file and extract actionable tasks."""
    
    def __init__(self, roadmap_path: str):
        self.roadmap_path = Path(roadmap_path)
        self.tasks: List[Task] = []
        
    def parse(self) -> List[Task]:
        """Parse the roadmap file and extract all tasks."""
        if not self.roadmap_path.exists():
            raise FileNotFoundError(f"Roadmap file not found: {self.roadmap_path}")
            
        with open(self.roadmap_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        lines = content.split('\n')
        current_phase = ""
        current_priority = ""
        current_section = ""
        
        i = 0
        while i < len(lines):
            line = lines[i]
            line_number = i + 1
            
            # Track current phase
            if line.startswith("### Phase"):
                phase_match = re.search(r'Phase \d+: ([^(]+)', line)
                if phase_match:
                    current_phase = phase_match.group(1).strip()
                    # Extract priority from the same line
                    if "HIGH PRIORITY" in line:
                        current_priority = "HIGH PRIORITY"
                    elif "MEDIUM PRIORITY" in line:
                        current_priority = "MEDIUM PRIORITY"
                    elif "FUTURE ROADMAP" in line:
                        current_priority = "FUTURE ROADMAP"
                    else:
                        current_priority = "NORMAL"
                        
            # Track current section
            elif line.startswith("#### "):
                current_section = line.replace("#### ", "").strip()
                
            # Look for tasks (checklist items)
            elif line.strip().startswith("- [ ]") or line.strip().startswith("- [x]"):
                task, lines_consumed = self._parse_task_with_details(lines, i, current_phase, current_priority, current_section)
                if task:
                    self.tasks.append(task)
                i += lines_consumed - 1  # Adjust for consumed lines
                
            i += 1
                    
        return self.tasks
    
    def _parse_task_with_details(self, lines: List[str], start_idx: int, phase: str, priority: str, section: str) -> tuple:
        """Parse a task line and collect its detailed sub-items."""
        line = lines[start_idx]
        line_number = start_idx + 1
        
        # Check if completed
        is_completed = line.strip().startswith("- [x]")
        
        # Extract task content
        content = re.sub(r'^- \[[x ]\] \*\*([^*]+)\*\*', r'\1', line.strip())
        if content == line.strip():  # No bold formatting
            content = re.sub(r'^- \[[x ]\] ', '', line.strip())
            
        if not content:
            return None, 1
            
        title = content.strip()
        # Clean up title
        title = re.sub(r'\*\*([^*]+)\*\*', r'\1', title)
        
        # Collect detailed descriptions from sub-items
        description_parts = []
        consumed_lines = 1
        
        # Look ahead for indented sub-items
        for i in range(start_idx + 1, len(lines)):
            next_line = lines[i]
            # If we hit another main task or section, stop
            if (next_line.strip().startswith("- [ ]") or 
                next_line.strip().startswith("- [x]") or
                next_line.startswith("#")):
                break
                
            # If it's an indented item, add to description
            if next_line.startswith("  - ") and next_line.strip():
                desc_item = next_line.strip().replace("- ", "").strip()
                description_parts.append(f"• {desc_item}")
                consumed_lines += 1
            elif next_line.strip() == "":
                consumed_lines += 1
            else:
                break
                
        description = "\n".join(description_parts) if description_parts else ""
        
        return Task(
            title=title,
            description=description,
            phase=phase,
            priority=priority,
            section=section,
            is_completed=is_completed,
            line_number=line_number
        ), consumed_lines
    
    def get_incomplete_tasks(self) -> List[Task]:
        """Get only incomplete tasks."""
        return [task for task in self.tasks if not task.is_completed]
    
    def get_high_priority_tasks(self) -> List[Task]:
        """Get high priority incomplete tasks."""
        return [task for task in self.get_incomplete_tasks() if "HIGH" in task.priority]

def main():
    """Main function to parse roadmap and output JSON for GitHub Action."""
    if len(sys.argv) != 2:
        print("Usage: python roadmap_parser.py <roadmap_file>")
        sys.exit(1)
        
    roadmap_file = sys.argv[1]
    
    try:
        parser = RoadmapParser(roadmap_file)
        tasks = parser.parse()
        
        # Get incomplete tasks only
        incomplete_tasks = parser.get_incomplete_tasks()
        
        # Convert to GitHub issues format
        issues = [task.to_issue_format() for task in incomplete_tasks]
        
        # Output as JSON for GitHub Action
        output = {
            "total_tasks": len(tasks),
            "incomplete_tasks": len(incomplete_tasks),
            "issues": issues[:10]  # Limit to first 10 to avoid overwhelming
        }
        
        print(json.dumps(output, indent=2))
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()