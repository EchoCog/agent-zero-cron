"""API endpoint for sending Inngest events."""

import json
from flask import request, jsonify
from datetime import datetime, timezone

from python.helpers.inngest_client import get_inngest_manager


def inngest_send_event():
    """Send an event to Inngest."""
    try:
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "Request body must be JSON"}), 400
        
        # Extract parameters
        event_name = data.get("name")
        event_data = data.get("data")
        user = data.get("user")
        ts = data.get("ts")
        
        # Validate required parameters
        if not event_name:
            return jsonify({"status": "error", "message": "Event name is required"}), 400
        
        if not event_data:
            return jsonify({"status": "error", "message": "Event data is required"}), 400
        
        if not isinstance(event_data, dict):
            return jsonify({"status": "error", "message": "Event data must be a dictionary"}), 400
        
        # Get Inngest manager
        inngest_manager = get_inngest_manager()
        
        if not inngest_manager.is_enabled():
            return jsonify({
                "status": "error", 
                "message": "Inngest is not enabled. Check configuration and INNGEST_EVENT_KEY."
            }), 400
        
        # Send event
        import asyncio
        success = asyncio.create_task(
            inngest_manager.send_event(event_name, event_data, user, ts)
        )
        
        # Wait for result
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(success)
        finally:
            loop.close()
        
        if result:
            return jsonify({
                "status": "success",
                "message": f"Event '{event_name}' sent successfully",
                "event_name": event_name,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
        else:
            return jsonify({
                "status": "error",
                "message": f"Failed to send event '{event_name}'"
            }), 500
            
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500