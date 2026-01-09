"""
Decorators for easy background task execution.

Provides simple decorator-based API for running methods in background.
"""
from typing import Callable, Optional, Any
from functools import wraps
import logging

from .worker import BackgroundTask

logger = logging.getLogger(__name__)


def run_in_background(
    task_name: Optional[str] = None,
    on_complete: Optional[Callable[[Any], None]] = None,
    on_error: Optional[Callable[[Exception], None]] = None,
    on_progress: Optional[Callable[[int, int, str], None]] = None,
    show_progress: bool = False
):
    """
    Decorator to run a method in background.

    Usage:
        class MyService:
            @run_in_background(
                task_name="Process Data",
                on_complete=self.handle_result
            )
            def process_large_dataset(self, data):
                # This runs in background
                result = heavy_processing(data)
                return result

            def handle_result(self, result):
                # This runs on UI thread
                self.display(result)

    Args:
        task_name: Human-readable task name
        on_complete: Callback for result (runs on UI thread)
        on_error: Callback for errors (runs on UI thread)
        on_progress: Callback for progress updates
        show_progress: Show default progress dialog

    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Determine task name
            name = task_name or f"{func.__name__}"

            # Create task
            task = BackgroundTask(
                func=func,
                args=args,
                kwargs=kwargs,
                task_name=name,
                on_complete=on_complete,
                on_error=on_error,
                on_progress=on_progress
            )

            # Start task
            task.start()

            # Return task (so caller can cancel if needed)
            return task

        return wrapper
    return decorator


def async_method(
    task_name: Optional[str] = None,
    show_progress: bool = True
):
    """
    Decorator to mark a method as async (runs in background).

    This is a simpler version of run_in_background for methods that:
    - Don't need callbacks
    - Just want to run in background without freezing UI

    Usage:
        class MyService:
            @async_method(task_name="Load Data")
            def load_large_file(self, path):
                # This runs in background automatically
                return self._load(path)

    Args:
        task_name: Human-readable task name
        show_progress: Show progress dialog

    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            name = task_name or f"{func.__name__}"

            task = BackgroundTask(
                func=func,
                args=args,
                kwargs=kwargs,
                task_name=name
            )

            task.start()
            return task

        return wrapper
    return decorator


class BackgroundMethod:
    """
    Descriptor for background methods (alternative to decorators).

    Allows defining background methods with full control over callbacks.

    Example:
        class MyService:
            def __init__(self):
                self.process_data = BackgroundMethod(
                    self._process_data_impl,
                    task_name="Process Data",
                    on_complete=self.on_process_complete
                )

            def _process_data_impl(self, data):
                # Background implementation
                return process(data)

            def on_process_complete(self, result):
                # UI thread callback
                self.display(result)

            # Usage:
            # self.process_data(my_data)  # Runs in background
    """

    def __init__(
        self,
        func: Callable,
        task_name: str,
        on_complete: Optional[Callable] = None,
        on_error: Optional[Callable] = None,
        on_progress: Optional[Callable] = None
    ):
        self.func = func
        self.task_name = task_name
        self.on_complete = on_complete
        self.on_error = on_error
        self.on_progress = on_progress

    def __call__(self, *args, **kwargs) -> BackgroundTask:
        """Execute the method in background."""
        task = BackgroundTask(
            func=self.func,
            args=args,
            kwargs=kwargs,
            task_name=self.task_name,
            on_complete=self.on_complete,
            on_error=self.on_error,
            on_progress=self.on_progress
        )
        task.start()
        return task
