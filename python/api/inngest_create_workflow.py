"""API endpoint for creating and triggering Inngest workflows."""

import json
import uuid
from flask import request, jsonify
from datetime import datetime, timezone

from python.helpers.task_workflow import get_task_workflow_manager


def inngest_create_workflow():
    """Create and trigger an Inngest workflow."""
    try:
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "Request body must be JSON"}), 400
        
        # Extract parameters
        workflow_id = data.get("workflow_id") or str(uuid.uuid4())
        workflow_definition = data.get("workflow_definition")
        workflow_input = data.get("workflow_input", {})
        
        # Validate required parameters
        if not workflow_definition:
            return jsonify({"status": "error", "message": "Workflow definition is required"}), 400
        
        if not isinstance(workflow_definition, dict):
            return jsonify({"status": "error", "message": "Workflow definition must be a dictionary"}), 400
        
        # Get workflow manager
        workflow_manager = get_task_workflow_manager()
        
        # Create workflow
        import asyncio
        success_task = asyncio.create_task(
            workflow_manager.create_workflow(workflow_id, workflow_definition, workflow_input)
        )
        
        # Wait for result
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            success = loop.run_until_complete(success_task)
        finally:
            loop.close()
        
        if success:
            return jsonify({
                "status": "success",
                "message": f"Workflow '{workflow_id}' created and triggered successfully",
                "workflow_id": workflow_id,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
        else:
            return jsonify({
                "status": "error",
                "message": f"Failed to create workflow '{workflow_id}'"
            }), 500
            
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500