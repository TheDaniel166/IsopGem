"""
Geometry ViewModel - The Mediator.
ViewModel mediating between GeometricShape model and UI panes with debounced auto-save.
"""
from typing import Optional, Dict
from PyQt6.QtCore import QObject, pyqtSignal, QTimer

from ...services.base_shape import GeometricShape, ShapeProperty
from ...services.persistence_service import PersistenceService

class GeometryViewModel(QObject):
    """
    ViewModel for Geometry Calculator.
    Mediates between the GeometricShape (Model) and the UI Panes (View).
    """
    
    # Signals
    property_changed = pyqtSignal(str, float)     # key, value (for feedback)
    calculation_completed = pyqtSignal()          # Emitted when a calculation finishes
    shape_cleared = pyqtSignal()                  # Emitted when all properties are cleared
    validation_error = pyqtSignal(str)            # message
    history_updated = pyqtSignal()                # Emitted when a save occurs
    
    def __init__(self, shape: GeometricShape):
        super().__init__()
        self._shape = shape
        self._updating = False
        
        # Debounced Auto-Save
        self._save_timer = QTimer()
        self._save_timer.setSingleShot(True)
        self._save_timer.setInterval(2000) # 2 seconds
        self._save_timer.timeout.connect(self.save_state)

    def save_state(self):
        """Manually trigger save (or auto-save hook)."""
        PersistenceService.save_calculation(self._shape)
        self.history_updated.emit()

    def load_state(self, data: Dict):
        """Load state from history entry data."""
        self._shape.from_dict(data)
        self.calculation_completed.emit()

    @property
    def shape_name(self) -> str:
        return self._shape.name

    @property
    def shape_description(self) -> str:
        return self._shape.description
    
    def get_properties(self) -> list[ShapeProperty]:
        return self._shape.get_all_properties()
    
    def get_shape(self) -> GeometricShape:
        """Access underlying shape for rendering (Scene needs direct access usually)."""
        return self._shape

    def set_property(self, key: str, value: float):
        """Attempt to set a property and trigger calculation."""
        if self._updating:
            return

        self._updating = True
        try:
            # Validate
            is_valid, error = self._shape.validate_value(key, value)
            if not is_valid:
                self.validation_error.emit(error)
                return

            # Set & Calculate
            success = self._shape.set_property(key, value)
            if success:
                self.calculation_completed.emit()
                # Trigger debounced save
                self._save_timer.start()
            else:
                # Calculation failed (e.g. impossible geometry)
                pass 
        finally:
            self._updating = False

    def clear_property(self, key: str):
        """Clear a single property value."""
        if key in self._shape.properties:
            self._shape.properties[key].value = None
            # Re-calculate? Usually clearing one might require clearing others or re-solving.
            # BaseShape logic is a bit manual.
            # For 2D shapes, usually we calculate FROM a property. 
            # If we clear inputs, we might need to clear derived.
            # Ideally shape.calculate_from_property handles this, but usually it takes a value.
            
            # Simple approach: clear all derived if input is cleared? 
            # Or just update view (which will show empty).
            self.calculation_completed.emit() 

    def clear_all(self):
        """Reset the shape."""
        self._shape.clear_all()
        self.shape_cleared.emit()
        self.calculation_completed.emit()
