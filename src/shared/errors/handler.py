"""
Error handling and recovery strategies.

Provides centralized error handling with:
- Structured logging
- Context tracking
- Recovery strategies
- User notification
"""
"""
SHARED JUSTIFICATION:
- RATIONALE: Core Infrastructure
- USED BY: Correspondences (4 references)
- CRITERION: 2 (Essential for app to function)
"""

from typing import Optional, Callable, Any, TypeVar, Dict
from contextlib import contextmanager
from dataclasses import dataclass, field
from functools import wraps
import logging
import traceback

from .base import AppError, ErrorSeverity, ErrorCategory
from .codes import ErrorCode, get_user_message
from .ui_notifier import notify_app_error, ask_retry

logger = logging.getLogger(__name__)

T = TypeVar('T')


@dataclass
class ErrorContext:
    """
    Context information for error handling.

    Tracks where and why an error occurred.
    """
    operation: str  # What operation was being performed
    component: str  # Which component (service, window, etc.)
    user_action: Optional[str] = None  # What the user was doing
    metadata: Dict[str, Any] = field(default_factory=dict)  # Additional context

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging."""
        return {
            "operation": self.operation,
            "component": self.component,
            "user_action": self.user_action,
            "metadata": self.metadata,
        }


def handle_error(
    error: Exception,
    context: Optional[ErrorContext] = None,
    notify_user: bool = True,
    fallback_value: Any = None,
    log_level: str = "error"
) -> Any:
    """
    Central error handling function.

    Args:
        error: The exception that occurred
        context: Optional context about where/why error occurred
        notify_user: Show error dialog to user
        fallback_value: Value to return on error
        log_level: Logging level (debug, info, warning, error, critical)

    Returns:
        fallback_value if provided, otherwise raises the error

    Example:
        try:
            result = risky_operation()
        except Exception as e:
            return handle_error(
                e,
                context=ErrorContext(
                    operation="load_lexicon",
                    component="LexiconService",
                    user_action="Opening lexicon lookup"
                ),
                fallback_value=[]
            )
    """
    # Convert to AppError if not already
    if not isinstance(error, AppError):
        app_error = AppError(
            code=ErrorCode.ERR_SYS_UNKNOWN,
            message=str(error),
            details=traceback.format_exc(),
            user_message=get_user_message(ErrorCode.ERR_SYS_UNKNOWN),
            cause=error,
        )
    else:
        app_error = error

    # Add context to error
    if context:
        app_error.context.update(context.to_dict())

    # Log the error
    log_func = getattr(logger, log_level)
    log_func(
        f"[{context.component if context else 'Unknown'}] {app_error.message}",
        extra=app_error.to_dict(),
        exc_info=app_error.cause if app_error.cause else None
    )

    # Notify user if requested
    if notify_user:
        notify_app_error(app_error)

    # Return fallback or raise
    if fallback_value is not None:
        return fallback_value
    else:
        raise app_error


@contextmanager
def error_boundary(
    operation: str,
    component: str,
    user_action: Optional[str] = None,
    fallback_value: Any = None,
    notify_user: bool = True,
    reraise: bool = False
):
    """
    Context manager for error handling boundaries.

    Use this to wrap risky operations with automatic error handling.

    Args:
        operation: Name of the operation
        component: Component performing operation
        user_action: What the user was doing
        fallback_value: Value to return on error
        notify_user: Show error to user
        reraise: Re-raise error after handling

    Example:
        with error_boundary(
            operation="load_lexicon",
            component="LexiconService",
            fallback_value=[]
        ):
            results = load_lexicon_file("hebrew")

        # If error occurs, fallback_value is returned
    """
    context = ErrorContext(
        operation=operation,
        component=component,
        user_action=user_action
    )

    try:
        yield
    except Exception as e:
        handle_error(
            e,
            context=context,
            notify_user=notify_user,
            fallback_value=fallback_value
        )

        if reraise:
            raise


def with_error_handling(
    operation: str,
    component: str,
    fallback_value: Any = None,
    notify_user: bool = True,
    retry_count: int = 0
):
    """
    Decorator for error handling on functions.

    Args:
        operation: Name of the operation
        component: Component performing operation
        fallback_value: Value to return on error
        notify_user: Show error to user
        retry_count: Number of times to retry on error

    Example:
        @with_error_handling(
            operation="lookup_word",
            component="LexiconService",
            fallback_value=[]
        )
        def lookup_hebrew(word: str) -> List[LexiconEntry]:
            # This will automatically handle errors
            return self._do_lookup(word)
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            context = ErrorContext(
                operation=operation,
                component=component,
                metadata={"args": str(args), "kwargs": str(kwargs)}
            )

            attempts = 0
            last_error = None

            while attempts <= retry_count:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    attempts += 1

                    # If we have retries left, ask user
                    if attempts <= retry_count:
                        if not isinstance(e, AppError):
                            app_error = AppError(
                                code=ErrorCode.ERR_SYS_UNKNOWN,
                                message=str(e),
                                cause=e
                            )
                        else:
                            app_error = e

                        if app_error.recoverable:
                            should_retry = ask_retry(
                                message=f"{app_error.user_message}\n\nWould you like to try again?",
                                details=app_error.details
                            )
                            if not should_retry:
                                break
                        else:
                            break

            # All retries exhausted or user declined
            return handle_error(
                last_error,
                context=context,
                notify_user=notify_user,
                fallback_value=fallback_value
            )

        return wrapper
    return decorator


def safe_call(
    func: Callable[..., T],
    *args,
    fallback: T = None,
    log_errors: bool = True,
    **kwargs
) -> T:
    """
    Safely call a function, returning fallback on error.

    Useful for quick one-off calls where you don't want exceptions.

    Args:
        func: Function to call
        *args: Positional arguments for func
        fallback: Value to return on error
        log_errors: Log errors that occur
        **kwargs: Keyword arguments for func

    Returns:
        Result of func() or fallback on error

    Example:
        # Instead of:
        try:
            result = risky_function()
        except:
            result = default_value

        # Use:
        result = safe_call(risky_function, fallback=default_value)
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        if log_errors:
            logger.warning(f"safe_call caught exception in {func.__name__}: {e}")
        return fallback


class RecoveryStrategy:
    """
    Base class for error recovery strategies.

    Subclass this to implement custom recovery logic.
    """

    def can_recover(self, error: AppError) -> bool:
        """Check if this strategy can recover from the error."""
        raise NotImplementedError

    def recover(self, error: AppError) -> Any:
        """Attempt to recover from the error."""
        raise NotImplementedError


class ClearCacheRecovery(RecoveryStrategy):
    """Recovery strategy: Clear caches and retry."""

    def can_recover(self, error: AppError) -> bool:
        return error.code in [
            ErrorCode.ERR_LEX_CACHE_FULL,
            ErrorCode.ERR_SYS_OUT_OF_MEMORY
        ]

    def recover(self, error: AppError) -> Any:
        """Clear caches and suggest retry."""
        from shared.services.lexicon.comprehensive_lexicon_service import ComprehensiveLexiconService

        # Clear lexicon caches
        service = ComprehensiveLexiconService()
        service.clear_caches()

        logger.info("Cleared lexicon caches for recovery")

        # Ask user to retry
        return ask_retry(
            message="Memory cleared. Would you like to try again?",
            details=error.details
        )


class ReloadFileRecovery(RecoveryStrategy):
    """Recovery strategy: Reload corrupted file."""

    def can_recover(self, error: AppError) -> bool:
        return error.code in [
            ErrorCode.ERR_DATA_FILE_CORRUPT,
            ErrorCode.ERR_LEX_INDEX_CORRUPT
        ]

    def recover(self, error: AppError) -> Any:
        """Attempt to reload file."""
        # In a real implementation, this would attempt to re-download
        # or regenerate the corrupted file
        return ask_retry(
            message="File may be corrupted. Please reinstall or try again.",
            details=error.details
        )


# Global recovery strategies
_recovery_strategies: list[RecoveryStrategy] = [
    ClearCacheRecovery(),
    ReloadFileRecovery(),
]


def attempt_recovery(error: AppError) -> bool:
    """
    Attempt to recover from an error using registered strategies.

    Args:
        error: The error to recover from

    Returns:
        True if recovery was successful, False otherwise
    """
    for strategy in _recovery_strategies:
        if strategy.can_recover(error):
            try:
                result = strategy.recover(error)
                if result:
                    logger.info(f"Successfully recovered from {error.code} using {strategy.__class__.__name__}")
                    return True
            except Exception as e:
                logger.warning(f"Recovery strategy {strategy.__class__.__name__} failed: {e}")

    return False