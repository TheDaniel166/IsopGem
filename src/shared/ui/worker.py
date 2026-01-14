"""
⚠️  GRANDFATHERED VIOLATION - Pre-existing before Law of Substrate (2026-01-13)

SHARED JUSTIFICATION:
- RATIONALE: GRANDFATHERED - Needs manual review
- USED BY: Astrology, Document_manager (9 references)
- CRITERION: Unknown - requires categorization

This module violates the Law of the Substrate but is documented as pre-existing.
Refactoring plan: See wiki/04_prophecies/shared_folder_audit_2026-01-13.md
"""

"""
Standardized Background Worker pattern for IsopGem.
Uses QRunnable + QThreadPool for concurrent execution without freezing the UI.
"""

import sys
import traceback
from typing import Callable, Any, Optional

from PyQt6.QtCore import QRunnable, QObject, pyqtSignal, pyqtSlot

class WorkerSignals(QObject):
    """
    Defines the signals available from a running worker thread.
    Supported signals are:
    
    finished
        No data
    
    error
        tuple (exctype, value, traceback.format_exc())
    
    result
        object data returned from processing, anything
    
    progress
        int indicating % progress 
    """
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    progress = pyqtSignal(int)

class BackgroundWorker(QRunnable):
    """
    Worker thread integration.
    
    Inherits from QRunnable to handle worker thread setup, signals and wrap-up.
    
    :param fn: The function callback to run on this worker thread. Supplied args and 
               kwargs will be passed through to the runner.
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function
    """

    def __init__(self, fn: Callable, *args: Any, **kwargs: Any):
        super(BackgroundWorker, self).__init__()
        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()
        
        # Add the 'progress_callback' parameter to the function kwargs
        # This allows the function to update progress if it accepts 'progress_callback'
        # Check if function accepts it, or just pass it blindly if designed so.
        # For generality, we won't inject it unless requested, or we rely on partials.
        # But a common pattern involves injecting self.signals.progress
        # We'll attach it to kwargs IF the user didn't provide one
        if 'progress_callback' not in self.kwargs:
            # We do NOT inject signal automatically anymore to avoid TypeError on simple functions.
            # Users must pass it explicitly via partial if needed.
            pass

    @pyqtSlot()
    def run(self):
        """
        Initialise the runner function with passed args, kwargs.
        """
        try:
            # We attempt to run the function
            # If function doesn't accept progress_callback, it might raise TypeError usually.
            # To be safe, we might try-catch argument errors if needed, but for now we trust usage.
            # Actually, standard pattern is strict. 
            # If target function doesn't use progress_callback, we should pop it?
            # Let's clean up: Only certain tailored functions expect it.
            # If we inject it blindly, generic functions fail. 
            # So: we DON'T inject automatically unless we know fn handles it.
            # Reverting automated injection.
            if 'progress_callback' in self.kwargs:
                pass # Already provided or we strip it? 
            else:
                pass 
                
            # If we really want progress, user should partial(fn, progress_callback=signals.progress)
            
            result = self.fn(*self.args, **self.kwargs)
        except Exception:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)
        finally:
            self.signals.finished.emit()