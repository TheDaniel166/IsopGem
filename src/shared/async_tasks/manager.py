"""
Task manager for tracking and controlling background tasks.

Provides centralized management of all background tasks:
- Track active tasks
- Cancel all tasks
- Monitor task status
- Task queue management
"""
from typing import List, Dict, Optional
from PyQt6.QtCore import QThreadPool, QObject, pyqtSignal
import logging

from .worker import BackgroundTask

logger = logging.getLogger(__name__)


class TaskManager(QObject):
    """
    Centralized manager for background tasks.

    Tracks all active tasks and provides control methods.

    Example:
        manager = TaskManager()

        # Start tasks
        task1 = manager.create_task(func1, task_name="Task 1")
        task2 = manager.create_task(func2, task_name="Task 2")

        # Monitor
        print(f"Active tasks: {manager.active_count()}")

        # Cancel all
        manager.cancel_all()
    """

    # Signals
    task_started = pyqtSignal(str)  # task_name
    task_completed = pyqtSignal(str)  # task_name
    task_failed = pyqtSignal(str, Exception)  # task_name, error
    task_cancelled = pyqtSignal(str)  # task_name

    def __init__(self, max_threads: int = 4):
        """
        Initialize task manager.

        Args:
            max_threads: Maximum number of concurrent threads
        """
        super().__init__()

        # Create dedicated thread pool
        self.thread_pool = QThreadPool()
        self.thread_pool.setMaxThreadCount(max_threads)

        # Track active tasks
        self.tasks: Dict[str, BackgroundTask] = {}
        self._task_counter = 0

        logger.info(f"TaskManager initialized with {max_threads} max threads")

    def create_task(
        self,
        func,
        args=(),
        kwargs=None,
        task_name: Optional[str] = None,
        **options
    ) -> BackgroundTask:
        """
        Create and start a background task.

        Args:
            func: Function to execute
            args: Positional arguments
            kwargs: Keyword arguments
            task_name: Human-readable name
            **options: Additional options (on_complete, on_error, etc.)

        Returns:
            BackgroundTask instance
        """
        # Generate unique task name
        if not task_name:
            self._task_counter += 1
            task_name = f"Task-{self._task_counter}"

        # Create task
        task = BackgroundTask(
            func=func,
            args=args,
            kwargs=kwargs or {},
            task_name=task_name,
            thread_pool=self.thread_pool,
            **options
        )

        # Connect signals for tracking
        task.worker.signals.started.connect(
            lambda: self._on_task_started(task_name)
        )
        task.worker.signals.finished.connect(
            lambda result: self._on_task_completed(task_name)
        )
        task.worker.signals.error.connect(
            lambda error: self._on_task_failed(task_name, error)
        )
        task.worker.signals.cancelled.connect(
            lambda: self._on_task_cancelled(task_name)
        )

        # Track task
        self.tasks[task_name] = task

        # Start task
        task.start()

        return task

    def cancel_task(self, task_name: str) -> bool:
        """
        Cancel a specific task.

        Args:
            task_name: Name of task to cancel

        Returns:
            True if task was cancelled, False if not found
        """
        task = self.tasks.get(task_name)
        if task:
            task.cancel()
            logger.info(f"Cancelled task: {task_name}")
            return True

        logger.warning(f"Task not found for cancellation: {task_name}")
        return False

    def cancel_all(self):
        """Cancel all active tasks."""
        logger.info(f"Cancelling {len(self.tasks)} active tasks")

        for task_name, task in list(self.tasks.items()):
            task.cancel()

        # Clear thread pool
        self.thread_pool.clear()

    def active_count(self) -> int:
        """Get number of active tasks."""
        return len(self.tasks)

    def active_tasks(self) -> List[str]:
        """Get list of active task names."""
        return list(self.tasks.keys())

    def wait_for_all(self, timeout_ms: int = 30000):
        """
        Wait for all tasks to complete.

        Args:
            timeout_ms: Timeout in milliseconds
        """
        self.thread_pool.waitForDone(timeout_ms)

    # Internal event handlers

    def _on_task_started(self, task_name: str):
        """Handle task started event."""
        logger.debug(f"Task started: {task_name}")
        self.task_started.emit(task_name)

    def _on_task_completed(self, task_name: str):
        """Handle task completed event."""
        logger.debug(f"Task completed: {task_name}")
        self.task_completed.emit(task_name)

        # Remove from tracking
        if task_name in self.tasks:
            del self.tasks[task_name]

    def _on_task_failed(self, task_name: str, error: Exception):
        """Handle task failed event."""
        logger.error(f"Task failed: {task_name} - {error}")
        self.task_failed.emit(task_name, error)

        # Remove from tracking
        if task_name in self.tasks:
            del self.tasks[task_name]

    def _on_task_cancelled(self, task_name: str):
        """Handle task cancelled event."""
        logger.info(f"Task cancelled: {task_name}")
        self.task_cancelled.emit(task_name)

        # Remove from tracking
        if task_name in self.tasks:
            del self.tasks[task_name]

    def __del__(self):
        """Cleanup on deletion."""
        self.cancel_all()
        self.thread_pool.waitForDone(5000)


# Global task manager instance
_task_manager: Optional[TaskManager] = None


def get_task_manager() -> TaskManager:
    """
    Get the global task manager instance.

    Returns:
        TaskManager singleton
    """
    global _task_manager

    if _task_manager is None:
        _task_manager = TaskManager()

    return _task_manager


def set_max_threads(count: int):
    """
    Set maximum number of concurrent background threads.

    Args:
        count: Maximum thread count
    """
    manager = get_task_manager()
    manager.thread_pool.setMaxThreadCount(count)
    logger.info(f"Max background threads set to: {count}")
