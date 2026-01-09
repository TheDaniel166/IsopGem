"""
Async/Background Task Manager for Isopgem.

This module provides background task execution without freezing the UI:
- QThreadPool-based workers for parallel execution
- Progress tracking with signals
- Task cancellation
- Error handling integration
- Result callbacks

Usage:
    from shared.async_tasks import BackgroundTask, run_in_background

    # Decorator approach
    @run_in_background(on_complete=handle_result)
    def long_operation(self, data):
        return process_large_dataset(data)

    # Manual approach
    task = BackgroundTask(
        func=enrich_lexicon,
        args=(lexicon_data,),
        on_complete=display_results,
        on_progress=update_progress
    )
    task.start()
"""

from .worker import BackgroundTask, BackgroundWorker
from .decorators import run_in_background, async_method
from .manager import TaskManager, get_task_manager

__all__ = [
    # Core task classes
    "BackgroundTask",
    "BackgroundWorker",

    # Decorators
    "run_in_background",
    "async_method",

    # Task manager
    "TaskManager",
    "get_task_manager",
]
