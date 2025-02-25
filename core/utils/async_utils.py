"""
IsopGem Async Utilities
Helper functions and decorators for async operations
"""
import asyncio
from functools import wraps
from typing import Callable, Any, Coroutine
from PyQt6.QtCore import QObject, pyqtSignal


def async_callback(f: Callable[..., Coroutine]) -> Callable[..., None]:
    """
    Decorator to handle async callbacks in Qt
    Ensures the coroutine is properly scheduled in the event loop
    """
    @wraps(f)
    def wrapper(*args: Any, **kwargs: Any) -> None:
        asyncio.create_task(f(*args, **kwargs))
    return wrapper


class AsyncWorker(QObject):
    """
    Helper class for running async tasks
    Provides signals for task completion and error handling
    """
    finished = pyqtSignal(object)
    error = pyqtSignal(Exception)
    
    def __init__(self, coro: Coroutine, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.coro = coro
        
    async def run(self) -> None:
        """Run the async task"""
        try:
            result = await self.coro
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(e)
