"""
Border Engine - The Architect of Boundaries.
Calculates cell border configurations based on selection topology and border style settings.
"""
from PyQt6.QtCore import Qt

class BorderEngine:
    """
    The Architect of Boundaries.
    Calculates which cells need which borders based on selection topology.
    Decouples the 'Math of Neighbors' from the 'UI of the Window'.
    """
    
    @staticmethod
    def calculate_borders(model, indexes, border_type, settings, border_role):  # type: ignore[reportMissingParameterType, reportUnknownParameterType]
        """
        Determines the new border configuration for a set of selected indexes.
        
        Args:
            model: The SpreadsheetModel (for reading existing data).
            indexes: List of QModelIndex.
            border_type: 'all', 'none', 'outside', 'top', etc.
            settings: Dict of border styling (color, width, style).
            border_role: The int Role ID for borders.
            
        Returns:
            List[Tuple[QModelIndex, dict]]: A list of (index, new_border_data) to apply.
        """
        if not indexes:
            return []
            
        updates = []
        selected_coords = set((idx.row(), idx.column()) for idx in indexes)  # type: ignore[reportUnknownArgumentType, reportUnknownMemberType, reportUnknownVariableType]
        
        for idx in indexes:
            if not idx.isValid(): continue
            
            r, c = idx.row(), idx.column()  # type: ignore[reportUnknownMemberType, reportUnknownVariableType]
            
            # Get existing borders (copy to avoid mutation)
            current_borders = model.data(idx, border_role) or {}
            if not isinstance(current_borders, dict): 
                current_borders = {}
            new_borders = current_borders.copy()
            
            # Use copy of settings to avoid shared references if we mutate later
            pen_config = settings.copy()
            
            if border_type == "none":
                new_borders = {}
                
            elif border_type == "all":
                new_borders["top"] = pen_config
                new_borders["bottom"] = pen_config
                new_borders["left"] = pen_config
                new_borders["right"] = pen_config
                
            elif border_type == "outside":
                # Check neighbors
                # Top: Apply if neighbor above is NOT selected
                if (r - 1, c) not in selected_coords:
                    new_borders["top"] = pen_config
                # Bottom: Apply if neighbor below is NOT selected
                if (r + 1, c) not in selected_coords:
                    new_borders["bottom"] = pen_config
                # Left: Apply if neighbor left is NOT selected
                if (r, c - 1) not in selected_coords:
                    new_borders["left"] = pen_config
                # Right: Apply if neighbor right is NOT selected
                if (r, c + 1) not in selected_coords:
                    new_borders["right"] = pen_config
                    
            elif border_type == "top": new_borders["top"] = pen_config
            elif border_type == "bottom": new_borders["bottom"] = pen_config
            elif border_type == "left": new_borders["left"] = pen_config
            elif border_type == "right": new_borders["right"] = pen_config
            
            updates.append((idx, new_borders))
            
        return updates

    @staticmethod
    def update_existing_borders(model, indexes, settings, border_role):  # type: ignore[reportMissingParameterType, reportUnknownParameterType]
        """
        Updates the STYLE (color, width) of existing borders without adding new ones.
        """
        if not indexes:
            return []
            
        updates = []
        
        for idx in indexes:
            if not idx.isValid(): continue
            
            current_borders = model.data(idx, border_role)
            if not current_borders or not isinstance(current_borders, dict):
                continue
            
            # Check what sides exist
            sides_to_update = [k for k in current_borders.keys() if k in ("top", "bottom", "left", "right")]
            if not sides_to_update:
                continue
                
            new_borders = current_borders.copy()
            
            for side in sides_to_update:
                new_borders[side] = settings.copy()
                
            updates.append((idx, new_borders))
            
        return updates
