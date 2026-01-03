"""
Persistence Service - The Chronicle.
Manages JSON file persistence for geometry calculation history and notes.
"""
import json
import os
import logging
from typing import List, Dict, Optional
from datetime import datetime

from .base_shape import GeometricShape

HISTORY_FILE = os.path.expanduser("~/.isopgem/geometry_history.json")

logger = logging.getLogger(__name__)

class PersistenceService:
    """
    The Chronicle: Manages persistence of geometry calculations.
    """
    
    @staticmethod
    def _ensure_history_file():
        if not os.path.exists(os.path.dirname(HISTORY_FILE)):
            os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
        if not os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, 'w') as f:
                json.dump([], f)

    @staticmethod
    def save_calculation(shape: GeometricShape):
        """Save the current state of a shape to history."""
        PersistenceService._ensure_history_file()
        
        # Generate Summary
        # Take up to 3 properties, preferring those with values
        summary_parts = []
        for prop in shape.get_all_properties():
            if prop.value is not None:
                # Format: "Radius: 5.0"
                # Skip internally used or default-looking values if needed, 
                # but for now just take the first few populated ones.
                val_str = f"{prop.value:.2f}" if isinstance(prop.value, float) else str(prop.value)
                summary_parts.append(f"{prop.name}: {val_str}")
        
        # Join top 3
        summary = " | ".join(summary_parts[:3])
        if not summary:
            summary = "No properties set"

        entry = {
            "timestamp": datetime.now().isoformat(),
            "shape_name": shape.name,
            "summary": summary,
            "note": "",
            "data": shape.to_dict()
        }
        
        try:
            with open(HISTORY_FILE, 'r') as f:
                history = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            history = []
            
        # Add new entry
        history.insert(0, entry)
        
        # Limit to 50
        history = history[:50]
        
        with open(HISTORY_FILE, 'w') as f:
            json.dump(history, f, indent=2)

    @staticmethod
    def update_note(timestamp: str, note_text: str):
        """Update the note for a specific history entry."""
        PersistenceService._ensure_history_file()
        try:
            with open(HISTORY_FILE, 'r') as f:
                history = json.load(f)
                
            updated = False
            for entry in history:
                if entry.get("timestamp") == timestamp:
                    entry["note"] = note_text
                    updated = True
                    break
            
            if updated:
                with open(HISTORY_FILE, 'w') as f:
                    json.dump(history, f, indent=2)
        except (OSError, json.JSONDecodeError, TypeError) as e:
            logger.warning(
                "Failed to update geometry note (%s): %s",
                type(e).__name__,
                e,
            )

    @staticmethod
    def delete_calculation(timestamp: str):
        """Delete a history entry by timestamp."""
        PersistenceService._ensure_history_file()
        try:
            with open(HISTORY_FILE, 'r') as f:
                history = json.load(f)
            
            # Filter out the item with matching timestamp
            new_history = [entry for entry in history if entry.get("timestamp") != timestamp]
            
            if len(new_history) < len(history):
                with open(HISTORY_FILE, 'w') as f:
                    json.dump(new_history, f, indent=2)
                    
        except (OSError, json.JSONDecodeError, TypeError) as e:
            logger.warning(
                "Failed to delete geometry history item (%s): %s",
                type(e).__name__,
                e,
            )

    @staticmethod
    def get_recent_calculations() -> List[Dict]:
        """Get list of recent calculations."""
        PersistenceService._ensure_history_file()
        try:
            with open(HISTORY_FILE, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError, OSError) as e:
            logger.warning(
                "Failed to read geometry history (%s): %s",
                type(e).__name__,
                e,
            )
            return []

    @staticmethod
    def clear_history():
        """
        Clear history logic.
        
        """
        with open(HISTORY_FILE, 'w') as f:
            json.dump([], f)