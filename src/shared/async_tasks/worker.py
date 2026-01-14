"""
Background worker implementation using QThreadPool.

Provides thread-based background execution with progress tracking and cancellation.
"""
"""
SHARED JUSTIFICATION:
- RATIONALE: Core Infrastructure
- USED BY: Astrology, Document_manager (10 references)
- CRITERION: 2 (Essential for app to function)
"""

from typing import Callable, Any, Optional, List
from PyQt6.QtCore import QObject, QRunnable, QThreadPool, pyqtSignal, pyqtSlot
import logging
import traceback
from functools import wraps

from shared.errors import AppError, ErrorCode, handle_error

logger = logging.getLogger(__name__)


class WorkerSignals(QObject):
    """
    Signals for background worker communication.

    These signals allow thread-safe communication between worker thread and UI thread.
    """
    # Emitted when task starts
    started = pyqtSignal()

    # Emitted with progress updates (current, total, message)
    progress = pyqtSignal(int, int, str)

    # Emitted when task completes successfully (result)
    finished = pyqtSignal(object)

    # Emitted when task fails (error)
    error = pyqtSignal(Exception)

    # Emitted when task is cancelled
    cancelled = pyqtSignal()


class BackgroundWorker(QRunnable):
    """
    Worker that executes a function in a background thread.

    Uses QThreadPool for efficient thread management.
    Integrates with error handling system.
    """

    def __init__(
        self,
        func: Callable,
        *args,
        task_name: str = "Background Task",
        **kwargs
    ):
        """
        Initialize worker.

        Args:
            func: Function to execute in background
            *args: Positional arguments for func
            task_name: Human-readable task name
            **kwargs: Keyword arguments for func
        """
        super().__init__()

        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.task_name = task_name
        self.signals = WorkerSignals()
        self._is_cancelled = False

        # Auto-delete when done
        self.setAutoDelete(True)

    @pyqtSlot()
    def run(self):
        """
        Execute the task in background thread.

        This runs in a separate thread - do NOT access UI directly!
        Use signals to communicate with UI.
        """
        try:
            logger.debug(f"Starting background task: {self.task_name}")
            self.signals.started.emit()

            # Execute function
            result = self.func(*self.args, **self.kwargs)

            # Check if cancelled before emitting result
            if self._is_cancelled:
                logger.debug(f"Task cancelled: {self.task_name}")
                self.signals.cancelled.emit()
                return

            # Success
            logger.debug(f"Task completed: {self.task_name}")
            self.signals.finished.emit(result)

        except Exception as e:
            # Handle error
            logger.error(f"Task failed: {self.task_name}", exc_info=True)

            # Convert to AppError if not already
            if not isinstance(e, AppError):
                error = AppError(
                    code=ErrorCode.ERR_SYS_UNKNOWN,
                    message=f"Background task failed: {str(e)}",
                    details=traceback.format_exc(),
                    cause=e,
                    context={"task": self.task_name}
                )
            else:
                error = e

            self.signals.error.emit(error)

    def cancel(self):
        """Request cancellation of this task."""
        self._is_cancelled = True
        logger.debug(f"Cancellation requested: {self.task_name}")

    def is_cancelled(self) -> bool:
        """Check if task has been cancelled."""
        return self._is_cancelled


class BackgroundTask:
    """
    High-level interface for background tasks.

    Provides a cleaner API than working with workers directly.

    Example:
        task = BackgroundTask(
            func=enrich_lexicon,
            args=(data,),
            task_name="Enrich Lexicon",
            on_complete=display_results,
            on_error=show_error,
            on_progress=update_progress
        )
        task.start()
    """

    def __init__(
        self,
        func: Callable,
        args: tuple = (),
        kwargs: dict = None,
        task_name: str = "Background Task",
        on_complete: Optional[Callable[[Any], None]] = None,
        on_error: Optional[Callable[[Exception], None]] = None,
        on_progress: Optional[Callable[[int, int, str], None]] = None,
        on_cancelled: Optional[Callable[[], None]] = None,
        thread_pool: Optional[QThreadPool] = None
    ):
        """
        Initialize background task.

        Args:
            func: Function to execute
            args: Positional arguments for func
            kwargs: Keyword arguments for func
            task_name: Human-readable name
            on_complete: Callback when task finishes (receives result)
            on_error: Callback when task fails (receives exception)
            on_progress: Callback for progress updates (current, total, message)
            on_cancelled: Callback when task is cancelled
            thread_pool: Custom thread pool (uses global pool if None)
        """
        self.func = func
        self.args = args
        self.kwargs = kwargs or {}
        self.task_name = task_name
        self.thread_pool = thread_pool or QThreadPool.globalInstance()

        # Create worker
        self.worker = BackgroundWorker(
            func=func,
            *args,
            task_name=task_name,
            **kwargs
        )

        # Connect callbacks
        if on_complete:
            self.worker.signals.finished.connect(on_complete)

        if on_error:
            self.worker.signals.error.connect(on_error)
        else:
            # Default error handler - log and show to user
            self.worker.signals.error.connect(self._default_error_handler)

        if on_progress:
            self.worker.signals.progress.connect(on_progress)

        if on_cancelled:
            self.worker.signals.cancelled.connect(on_cancelled)

    def start(self):
        """Start the background task."""
        logger.info(f"Starting background task: {self.task_name}")
        self.thread_pool.start(self.worker)

    def cancel(self):
        """Request cancellation of the task."""
        self.worker.cancel()

    def is_cancelled(self) -> bool:
        """Check if task has been cancelled."""
        return self.worker.is_cancelled()

    def _default_error_handler(self, error: Exception):
        """Default error handler - integrates with error handling system."""
        from shared.errors import notify_app_error

        if isinstance(error, AppError):
            notify_app_error(error)
        else:
            handle_error(
                error,
                notify_user=True,
                log_level="error"
            )


def progress_callback(worker: BackgroundWorker):
    """
    Helper to create progress callback for worker.

    Use this inside your background function to report progress.

    Example:
        def long_task(data):
            report_progress = progress_callback(current_worker)

            for i, item in enumerate(data):
                if current_worker.is_cancelled():
                    return None

                process(item)
                report_progress(i + 1, len(data), f"Processing {item}")

            return results
    """
    def report(current: int, total: int, message: str = ""):
        """Report progress."""
        if not worker.is_cancelled():
            worker.signals.progress.emit(current, total, message)

    return report