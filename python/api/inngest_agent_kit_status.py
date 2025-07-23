"""API endpoint for Inngest Agent Kit status."""

import json
from flask import jsonify

from python.helpers.inngest_client import get_inngest_agent_kit


def inngest_agent_kit_status():
    """Get Inngest Agent Kit status."""
    try:
        agent_kit = get_inngest_agent_kit()
        status = agent_kit.get_status()
        
        return jsonify({"status": "success", "data": status})
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500