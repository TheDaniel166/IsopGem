"""
Centralized error handling for Isopgem.

This module provides:
- Structured error types with error codes
- User-friendly error messages
- Error recovery strategies
- Logging integration
- UI notification helpers

Usage:
    from shared.errors import AppError, ErrorCode, handle_error

    try:
        result = risky_operation()
    except Exception as e:
        raise AppError(
            code=ErrorCode.LEXICON_NOT_FOUND,
            message="Could not load Hebrew lexicon",
            details=str(e),
            recoverable=True
        )
"""

from .base import AppError, ErrorSeverity, ErrorCategory
from .codes import ErrorCode
from .handler import handle_error, ErrorContext
from .ui_notifier import notify_error, notify_warning, notify_info, notify_success

__all__ = [
    # Base error types
    "AppError",
    "ErrorSeverity",
    "ErrorCategory",

    # Error codes
    "ErrorCode",

    # Error handling
    "handle_error",
    "ErrorContext",

    # UI notifications
    "notify_error",
    "notify_warning",
    "notify_info",
    "notify_success",
]
