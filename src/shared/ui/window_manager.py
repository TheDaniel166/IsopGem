"""Centralized window manager for IsopGem application.

This module manages the lifecycle of tool windows across all pillars,
including opening, closing, positioning, and tracking active windows.

The WindowManager also listens to the NavigationBus for decoupled window
requests, performing lazy imports to preserve pillar sovereignty.
"""
from typing import Dict, Optional, Type, Any
import logging
import importlib
from PyQt6.QtWidgets import QWidget, QMainWindow, QApplication
from PyQt6.QtCore import Qt, QTimer
# Import signal bus and registry
from shared.signals.navigation_bus import navigation_bus, get_window_info


logger = logging.getLogger(__name__)


class WindowManager:
    """Manages tool windows across the entire application."""
    
    def __init__(self, parent: Optional[QWidget] = None):
        """
        Initialize the window manager.
        
        Args:
            parent: Optional parent widget for the windows
        """
        self.parent = parent
        self._active_windows: Dict[str, QWidget] = {}
        self._window_counters: Dict[str, int] = {}  # Track instance counts per window type
        
        # Subscribe to navigation requests
        navigation_bus.request_window.connect(self._on_navigation_request)
    
    def open_window(
        self, 
        window_type: str,
        window_class: Type[QWidget], 
        allow_multiple: bool = True,
        *args, 
        **kwargs
    ) -> QWidget:
        """
        Open a tool window, allowing multiple instances if specified.
        
        Args:
            window_type: Type identifier for this window (e.g., 'gematria_calculator')
            window_class: The window class to instantiate
            allow_multiple: If True, creates new instance each time. If False, reuses existing.
            *args: Positional arguments for window constructor
            **kwargs: Keyword arguments for window constructor
            
        Returns:
            The window instance (new or existing)
        """
        # Generate unique window ID
        if allow_multiple:
            # Increment counter for this window type
            if window_type not in self._window_counters:
                self._window_counters[window_type] = 0
            self._window_counters[window_type] += 1
            window_id = f"{window_type}_{self._window_counters[window_type]}"
        else:
            # Single instance mode - check if already open
            window_id = window_type
            if window_id in self._active_windows:
                window = self._active_windows[window_id]
                # Bring to front and focus; ensure it is visible
                window.show()
                window.raise_()
                window.activateWindow()
                logger.debug("Reusing existing window %s (id=%s)", window_type, window_id)
                return window
        
        # Create new window
        # Pass parent=None to ensure the window is a top-level independent window
        # This is critical for multi-monitor support so the OS doesn't bind it to the main window
        window = window_class(*args, parent=None, **kwargs)
        
        # Store window type for later reference
        window.setProperty("window_type", window_type)
        window.setProperty("window_id", window_id)
        
        # Don't set parent to avoid Wayland issues
        # window.setParent(self.parent)
        
        # Configure window
        window.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        # Prevent tool windows from closing the entire application
        window.setAttribute(Qt.WidgetAttribute.WA_QuitOnClose, False)
        
        # Use Window type for independent behavior (allows taskbar entry and multi-monitor movement)
        window.setWindowFlags(
            Qt.WindowType.Window |
            Qt.WindowType.WindowCloseButtonHint |
            Qt.WindowType.WindowMinimizeButtonHint |
            Qt.WindowType.WindowMaximizeButtonHint |
            Qt.WindowType.WindowTitleHint |
            Qt.WindowType.WindowSystemMenuHint
        )
        
        # Track window closure
        window.destroyed.connect(lambda: self._on_window_closed(window_id))
        
        # Store reference
        self._active_windows[window_id] = window
        
        # Update window title to show instance number if multiple allowed
        if allow_multiple and self._window_counters[window_type] > 1:
            original_title = window.windowTitle()
            window.setWindowTitle(f"{original_title} #{self._window_counters[window_type]}")
        
        # Show the window handles
        window.show()
        
        # IMPORTANT: We purposefully DO NOT set the transient parent here.
        # Setting a transient parent (on Linux/X11) often locks the child window
        # to the same monitor as the parent and prevents independent movement.
        # By leaving them independent, the user gains full multi-monitor control.
        
        window.raise_()
        window.activateWindow()
        
        logger.debug("Opened window %s (id=%s)", window_type, window_id)
        
        return window
    
    def close_window(self, window_id: str) -> bool:
        """
        Close a specific window by ID.
        
        Args:
            window_id: The window identifier
            
        Returns:
            True if window was closed, False if not found
        """
        if window_id in self._active_windows:
            window = self._active_windows[window_id]
            window.close()
            # If the window doesn't emit destroyed immediately (offscreen/minimal plugins),
            # proactively remove the reference so callers observe accurate state.
            try:
                del self._active_windows[window_id]
            except KeyError:
                pass
            logger.debug("Closed window id=%s", window_id)
            return True
        return False
    
    def close_all_windows(self):
        """Close all managed windows."""
        # Create list of IDs to avoid dict size change during iteration
        window_ids = list(self._active_windows.keys())
        for window_id in window_ids:
            self.close_window(window_id)

    def close_windows_of_type(self, window_type: str) -> int:
        """
        Close all open windows matching a given window type.

        Args:
            window_type: The type of window to close (e.g., 'gematria_calculator')

        Returns:
            The number of windows closed
        """
        closed = 0
        # Copy keys to avoid mutation during iteration
        for wid, window in list(self._active_windows.items()):
            if window.property('window_type') == window_type:
                self.close_window(wid)
                closed += 1
        logger.debug("Closed %d windows of type %s", closed, window_type)
        return closed
    
    def is_window_open(self, window_id: str) -> bool:
        """
        Check if a window is currently open.
        
        Args:
            window_id: The window identifier
            
        Returns:
            True if window is open
        """
        return window_id in self._active_windows
    
    def get_window(self, window_id: str) -> Optional[QWidget]:
        """
        Get reference to an open window.
        
        Args:
            window_id: The window identifier
            
        Returns:
            The window instance or None if not found
        """
        return self._active_windows.get(window_id)
    
    def _on_window_closed(self, window_id: str):
        """
        Internal callback when a window is closed.
        
        Args:
            window_id: The window identifier
        """
        if window_id in self._active_windows:
            del self._active_windows[window_id]
    
    def get_active_windows(self) -> Dict[str, QWidget]:
        """
        Get all currently active windows.
        
        Returns:
            Dictionary of window_id -> window instance
        """
        return self._active_windows.copy()
    
    def get_window_count(self) -> int:
        """
        Get the number of currently open windows.
        
        Returns:
            Number of active windows
        """
        return len(self._active_windows)

    def raise_all_windows(self):
        """
        Bring all active windows to the front.
        """
        def do_raise():
            windows = list(self._active_windows.values())
            visible = [w for w in windows if w.isVisible()]
            
            for window in visible:
                window.raise_()
            
            # Note: We do NOT activate the last window here, as that would steal
            # focus from the main window if the user just clicked it.
            # window.raise_() is sufficient to bring them to view.
            
            logger.debug("Raised %d active windows", len(visible))
        
        # Small delay to ensure proper timing after tab changes
        QTimer.singleShot(50, do_raise)

    def _on_navigation_request(self, window_key: str, params: Dict[str, Any]):
        """
        Handle navigation requests from the signal bus.
        
        Performs lazy import of the requested window class to prevent
        circular imports and preserve pillar sovereignty.
        
        Args:
            window_key: Identifier from WINDOW_REGISTRY
            params: Parameters to pass to the window constructor
        """
        try:
            # Look up window info
            info = get_window_info(window_key)
            module_name = info["module"]
            class_name = info["class"]
            allow_multiple = info.get("allow_multiple", True)
            
            # Lazy Import
            try:
                module = importlib.import_module(module_name)
                window_class = getattr(module, class_name)
            except (ImportError, AttributeError) as e:
                logger.error(f"Failed to load window '{window_key}': {e}")
                return

            # Open the window
            # We filter params? Or pass all? 
            # Most windows accept specific args. Some might just take **kwargs.
            # Ideally, the registry might specify param mapping, but for now we rely on
            # windows accepting **kwargs or specific matching args.
            
            # Note: We pass window_manager=self if the class expects it.
            # Many of our hubs/windows take 'window_manager' as arg.
            # We can inspect the constructor or just try passing it if we want to be robust,
            # but standard pattern is explicit args.
            
            # Let's inject window_manager into params if not present, as most navigation targets need it.
            if "window_manager" not in params:
                 params["window_manager"] = self

            # Open
            self.open_window(
                window_type=window_key,
                window_class=window_class,
                allow_multiple=allow_multiple,
                **params
            )
            
        except Exception as e:
            logger.exception(f"Error handling navigation request for '{window_key}': {e}")
