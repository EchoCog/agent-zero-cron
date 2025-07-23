"""API endpoint for Inngest status."""

import json
from flask import jsonify

from python.helpers.inngest_client import get_inngest_manager, get_inngest_agent_kit
from python.helpers.task_workflow import get_task_workflow_manager


def inngest_status():
    """Get Inngest and workflow manager status."""
    try:
        # Get managers
        inngest_manager = get_inngest_manager()
        workflow_manager = get_task_workflow_manager()
        agent_kit = get_inngest_agent_kit()
        
        # Get status
        status = {
            "inngest": inngest_manager.get_status(),
            "workflow_manager": workflow_manager.get_status(),
            "agent_kit": agent_kit.get_status()
        }
        
        return jsonify({"status": "success", "data": status})
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500