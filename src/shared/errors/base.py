"""
Base error classes for Isopgem.

Defines the fundamental error types and structures used throughout the application.
"""
"""
SHARED JUSTIFICATION:
- RATIONALE: Core Infrastructure
- USED BY: Astrology, Correspondences, Document_manager, Gematria, Geometry, Time_mechanics, Tq, Tq_lexicon (105 references)
- CRITERION: 2 (Essential for app to function)
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Dict, Any
import traceback


class ErrorSeverity(Enum):
    """
    Severity levels for errors.

    Controls how errors are displayed to users and logged.
    """
    DEBUG = "debug"         # Development only
    INFO = "info"           # Informational, not an error
    WARNING = "warning"     # Something unexpected but handled
    ERROR = "error"         # Error that impacts functionality
    CRITICAL = "critical"   # Critical error, may crash app


class ErrorCategory(Enum):
    """
    Categories of errors for organization and filtering.
    """
    # Data access errors
    FILE_NOT_FOUND = "file_not_found"
    PARSE_ERROR = "parse_error"
    DATABASE_ERROR = "database_error"

    # Service errors
    LEXICON_ERROR = "lexicon_error"
    ETYMOLOGY_ERROR = "etymology_error"
    CALCULATION_ERROR = "calculation_error"
    GEOMETRY_ERROR = "geometry_error"

    # Network errors
    NETWORK_ERROR = "network_error"
    API_ERROR = "api_error"

    # UI errors
    RENDER_ERROR = "render_error"
    VALIDATION_ERROR = "validation_error"

    # System errors
    MEMORY_ERROR = "memory_error"
    PERMISSION_ERROR = "permission_error"
    CONFIGURATION_ERROR = "configuration_error"

    # Unknown
    UNKNOWN = "unknown"


@dataclass
class AppError(Exception):
    """
    Base application error with structured information.

    This replaces scattered exception handling with a consistent approach:
    - Error codes for identification
    - User-friendly messages
    - Technical details for logging
    - Recovery strategies
    - Context for debugging

    Example:
        raise AppError(
            code=ErrorCode.LEXICON_NOT_FOUND,
            message="Could not load Hebrew lexicon",
            details="File not found: /data/lexicons/hebrew_compact.json.gz",
            user_message="The Hebrew lexicon file is missing. Please reinstall.",
            recoverable=True,
            context={"language": "hebrew", "file": "hebrew_compact.json.gz"}
        )
    """
    # Required fields
    code: str  # From ErrorCode enum
    message: str  # Technical message (for logs)

    # Optional fields
    details: Optional[str] = None  # Additional technical details
    user_message: Optional[str] = None  # User-friendly message (for UI)
    severity: ErrorSeverity = ErrorSeverity.ERROR
    category: ErrorCategory = ErrorCategory.UNKNOWN
    recoverable: bool = False  # Can the user recover from this?

    # Context and debugging
    context: Dict[str, Any] = field(default_factory=dict)  # Additional context
    cause: Optional[Exception] = None  # Original exception
    stack_trace: Optional[str] = None

    def __post_init__(self):
        """Capture stack trace and set defaults."""
        # Capture stack trace if not provided
        if self.stack_trace is None:
            self.stack_trace = ''.join(traceback.format_stack()[:-1])

        # Use message as user_message if not provided
        if self.user_message is None:
            self.user_message = self.message

        # Call Exception.__init__ for proper exception behavior
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary (for logging/serialization)."""
        return {
            "code": self.code,
            "message": self.message,
            "details": self.details,
            "user_message": self.user_message,
            "severity": self.severity.value,
            "category": self.category.value,
            "recoverable": self.recoverable,
            "context": self.context,
            "cause": str(self.cause) if self.cause else None,
        }

    def __str__(self) -> str:
        """String representation for logging."""
        parts = [f"[{self.code}] {self.message}"]

        if self.details:
            parts.append(f"Details: {self.details}")

        if self.context:
            parts.append(f"Context: {self.context}")

        if self.cause:
            parts.append(f"Caused by: {self.cause}")

        return " | ".join(parts)


# Convenience subclasses for common error types

class DataError(AppError):
    """Error related to data access (files, database)."""
    def __init__(self, **kwargs):
        super().__init__(
            category=kwargs.pop("category", ErrorCategory.FILE_NOT_FOUND),
            **kwargs
        )


class ServiceError(AppError):
    """Error in a service layer."""
    def __init__(self, **kwargs):
        super().__init__(
            category=kwargs.pop("category", ErrorCategory.LEXICON_ERROR),
            **kwargs
        )


class NetworkError(AppError):
    """Network or API error."""
    def __init__(self, **kwargs):
        super().__init__(
            category=kwargs.pop("category", ErrorCategory.NETWORK_ERROR),
            severity=ErrorSeverity.WARNING,  # Network errors are often recoverable
            recoverable=True,
            **kwargs
        )


class ValidationError(AppError):
    """User input validation error."""
    def __init__(self, **kwargs):
        super().__init__(
            category=ErrorCategory.VALIDATION_ERROR,
            severity=ErrorSeverity.WARNING,
            recoverable=True,
            **kwargs
        )