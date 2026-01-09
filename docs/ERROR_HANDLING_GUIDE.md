## Error Handling Guide

Isopgem has a centralized error handling system that provides:
- Structured error types with error codes
- User-friendly notifications
- Automatic logging with context
- Error recovery strategies

---

## Quick Start

### Basic Usage

```python
from shared.errors import AppError, ErrorCode, handle_error

try:
    result = load_lexicon_file("hebrew")
except FileNotFoundError as e:
    raise AppError(
        code=ErrorCode.ERR_LEX_FILE_NOT_FOUND,
        message=f"Hebrew lexicon not found: {e}",
        user_message="The Hebrew lexicon file is missing. Please reinstall.",
        recoverable=False,
        context={"language": "hebrew", "file": str(e)}
    )
```

### Using Error Boundaries

```python
from shared.errors import error_boundary

def load_lexicon(language: str):
    with error_boundary(
        operation="load_lexicon",
        component="LexiconService",
        user_action=f"Loading {language} lexicon",
        fallback_value=[]
    ):
        # Risky operation
        data = load_file(f"{language}_lexicon.json.gz")
        return parse_lexicon(data)

    # If error occurs, fallback_value ([]) is returned
    # Error is logged and user is notified automatically
```

### Using Decorators

```python
from shared.errors import with_error_handling

class LexiconService:
    @with_error_handling(
        operation="lookup_word",
        component="LexiconService",
        fallback_value=[],
        retry_count=1  # Ask user to retry once
    )
    def lookup_hebrew(self, word: str) -> List[LexiconEntry]:
        """
        This method is automatically wrapped with error handling.

        - Errors are caught and logged
        - User is notified
        - Fallback value [] is returned on error
        - If recoverable, user is asked to retry
        """
        return self._do_lookup(word)
```

---

## Error Types

### AppError - Base Error

```python
from shared.errors import AppError, ErrorCode, ErrorSeverity

raise AppError(
    code=ErrorCode.ERR_LEX_FILE_NOT_FOUND,        # Error code (for tracking)
    message="Failed to load Hebrew lexicon",       # Technical message (logs)
    user_message="Hebrew lexicon is missing",      # User-friendly message (UI)
    details="FileNotFoundError: hebrew_compact.json.gz",  # Technical details
    severity=ErrorSeverity.ERROR,                  # Severity level
    recoverable=False,                             # Can user recover?
    context={"language": "hebrew"}                 # Additional context
)
```

### Convenience Subclasses

```python
from shared.errors import DataError, ServiceError, NetworkError, ValidationError

# Data access errors
raise DataError(
    code=ErrorCode.ERR_DATA_FILE_NOT_FOUND,
    message="Lexicon file not found",
    user_message="Required data file is missing"
)

# Service errors
raise ServiceError(
    code=ErrorCode.ERR_LEX_LOOKUP_FAILED,
    message="Lexicon lookup failed",
    user_message="Failed to look up word"
)

# Network errors (automatically marked as recoverable)
raise NetworkError(
    code=ErrorCode.ERR_NET_TIMEOUT,
    message="Sefaria API timeout",
    user_message="Network request timed out. Please try again."
)

# Validation errors
raise ValidationError(
    code=ErrorCode.ERR_VAL_REQUIRED_FIELD,
    message="Missing required field: word",
    user_message="Please enter a word to search"
)
```

---

## Error Codes

All error codes are defined in `ErrorCode` class:

```python
from shared.errors import ErrorCode

# Lexicon errors
ErrorCode.ERR_LEX_FILE_NOT_FOUND
ErrorCode.ERR_LEX_PARSE_FAILED
ErrorCode.ERR_LEX_LOOKUP_FAILED
ErrorCode.ERR_LEX_NO_RESULTS
ErrorCode.ERR_LEX_CACHE_FULL

# Etymology errors
ErrorCode.ERR_ETY_DB_NOT_FOUND
ErrorCode.ERR_ETY_LOOKUP_FAILED
ErrorCode.ERR_ETY_API_FAILED

# Gematria errors
ErrorCode.ERR_GEM_INVALID_INPUT
ErrorCode.ERR_GEM_CALCULATION_FAILED
ErrorCode.ERR_GEM_CIPHER_NOT_FOUND

# Document errors
ErrorCode.ERR_DOC_NOT_FOUND
ErrorCode.ERR_DOC_SAVE_FAILED
ErrorCode.ERR_DOC_LOAD_FAILED

# Network errors
ErrorCode.ERR_NET_CONNECTION_FAILED
ErrorCode.ERR_NET_TIMEOUT
ErrorCode.ERR_NET_API_ERROR

# ... and many more (see codes.py)
```

---

## User Notifications

### Manual Notifications

```python
from shared.errors import notify_error, notify_warning, notify_info, notify_success

# Error notification
notify_error(
    message="Failed to load lexicon",
    details="File not found: hebrew_compact.json.gz",
    title="Lexicon Error"
)

# Warning
notify_warning(
    message="Lexicon cache is getting full",
    details="Using 80MB of 100MB limit"
)

# Info (with auto-close)
notify_info(
    message="Lexicon loaded successfully",
    timeout_ms=2000  # Auto-close after 2 seconds
)

# Success (auto-closes)
notify_success(
    message="Document saved",
    timeout_ms=1500
)
```

### Automatic Notifications

```python
from shared.errors import AppError, handle_error

try:
    load_lexicon()
except Exception as e:
    # This automatically shows error dialog to user
    handle_error(
        e,
        context=ErrorContext(operation="load_lexicon", component="LexiconService"),
        notify_user=True  # Show dialog
    )
```

---

## Logging

Errors are automatically logged with context:

```python
from shared.errors import handle_error, ErrorContext

try:
    result = risky_operation()
except Exception as e:
    handle_error(
        e,
        context=ErrorContext(
            operation="calculate_gematria",
            component="GematriaCalculator",
            user_action="User clicked Calculate button",
            metadata={"input": "שלום", "cipher": "Standard"}
        )
    )

# Logs:
# [GematriaCalculator] Error in calculate_gematria
# Context: {operation: "calculate_gematria", user_action: "...", metadata: {...}}
```

---

## Error Recovery

### Automatic Recovery

Some errors have automatic recovery strategies:

```python
from shared.errors import AppError, ErrorCode

# This error triggers ClearCacheRecovery
raise AppError(
    code=ErrorCode.ERR_LEX_CACHE_FULL,
    message="Lexicon cache is full",
    user_message="Out of memory. Clearing cache...",
    recoverable=True
)

# Recovery strategy:
# 1. Clears lexicon caches
# 2. Asks user if they want to retry
# 3. If yes, operation continues
```

### Custom Recovery Strategies

```python
from shared.errors.handler import RecoveryStrategy, AppError

class MyRecoveryStrategy(RecoveryStrategy):
    def can_recover(self, error: AppError) -> bool:
        return error.code == ErrorCode.ERR_MY_CUSTOM_ERROR

    def recover(self, error: AppError) -> Any:
        # Custom recovery logic
        fix_the_problem()
        return True  # Recovery successful

# Register strategy
from shared.errors.handler import _recovery_strategies
_recovery_strategies.append(MyRecoveryStrategy())
```

---

## Real-World Examples

### Example 1: Lexicon Service

```python
from shared.errors import AppError, ErrorCode, with_error_handling
from shared.errors.handler import ErrorContext
from pathlib import Path

class LexiconService:
    @with_error_handling(
        operation="load_lexicon",
        component="LexiconService",
        fallback_value=None,
        retry_count=1
    )
    def load_lexicon(self, language: str):
        """Load lexicon with automatic error handling."""
        file_path = self.get_lexicon_path(language)

        # Check if file exists
        if not file_path.exists():
            raise AppError(
                code=ErrorCode.ERR_LEX_FILE_NOT_FOUND,
                message=f"Lexicon file not found: {file_path}",
                user_message=f"The {language} lexicon is missing. Please reinstall Isopgem.",
                details=f"Expected path: {file_path}",
                recoverable=False,
                context={"language": language, "path": str(file_path)}
            )

        # Try to parse
        try:
            data = json.loads(gzip.open(file_path).read())
            return data
        except json.JSONDecodeError as e:
            raise AppError(
                code=ErrorCode.ERR_LEX_PARSE_FAILED,
                message=f"Failed to parse lexicon: {e}",
                user_message=f"The {language} lexicon file is corrupted.",
                details=str(e),
                recoverable=False,
                cause=e,
                context={"language": language}
            )
```

### Example 2: Etymology Service with Network

```python
from shared.errors import NetworkError, ErrorCode, handle_error

class EtymologyService:
    def fetch_from_api(self, word: str):
        """Fetch etymology from API with error handling."""
        try:
            response = requests.get(
                f"https://api.example.com/etymology/{word}",
                timeout=5
            )
            response.raise_for_status()
            return response.json()

        except requests.Timeout:
            raise NetworkError(
                code=ErrorCode.ERR_NET_TIMEOUT,
                message=f"API request timed out for word: {word}",
                user_message="Network request timed out. Please check your connection and try again.",
                recoverable=True,  # User can retry
                context={"word": word, "api": "etymology"}
            )

        except requests.RequestException as e:
            raise NetworkError(
                code=ErrorCode.ERR_NET_API_ERROR,
                message=f"API request failed: {e}",
                user_message="Failed to connect to etymology service. Please try again later.",
                details=str(e),
                recoverable=True,
                cause=e,
                context={"word": word}
            )
```

### Example 3: Document Service with Database

```python
from shared.errors import DataError, ErrorCode, error_boundary

class DocumentService:
    def save_document(self, document):
        """Save document with error boundary."""
        with error_boundary(
            operation="save_document",
            component="DocumentService",
            user_action=f"Saving document '{document.title}'",
            notify_user=True
        ):
            # Validate
            if not document.title:
                raise ValidationError(
                    code=ErrorCode.ERR_VAL_REQUIRED_FIELD,
                    message="Document title is required",
                    user_message="Please provide a document title",
                    recoverable=True
                )

            # Save to database
            try:
                session = get_db_session()
                session.add(document)
                session.commit()
            except Exception as e:
                raise DataError(
                    code=ErrorCode.ERR_DB_TRANSACTION_FAILED,
                    message=f"Failed to save document: {e}",
                    user_message="Failed to save document. Please try again.",
                    details=str(e),
                    recoverable=True,
                    cause=e,
                    context={"document_id": document.id}
                )

            notify_success(f"Document '{document.title}' saved successfully")
```

---

## Best Practices

### 1. Use Specific Error Codes

```python
# ✓ GOOD
raise AppError(
    code=ErrorCode.ERR_LEX_FILE_NOT_FOUND,
    message="Hebrew lexicon not found"
)

# ✗ BAD
raise Exception("Lexicon not found")
```

### 2. Provide User-Friendly Messages

```python
# ✓ GOOD
raise AppError(
    code=ErrorCode.ERR_NET_TIMEOUT,
    message="API timeout after 5 seconds",  # Technical (logs)
    user_message="Network request timed out. Please check your connection."  # User-friendly
)

# ✗ BAD
raise Exception("requests.exceptions.Timeout: HTTPConnectionPool...")
```

### 3. Add Context

```python
# ✓ GOOD
raise AppError(
    code=ErrorCode.ERR_GEM_CALCULATION_FAILED,
    message="Calculation failed",
    context={"word": "שלום", "cipher": "Standard", "language": "Hebrew"}
)

# ✗ BAD
raise Exception("Calculation failed")  # No context - hard to debug
```

### 4. Mark Recoverable Errors

```python
# ✓ GOOD - User can retry network errors
raise NetworkError(
    code=ErrorCode.ERR_NET_TIMEOUT,
    message="Timeout",
    recoverable=True  # System will offer retry
)

# ✓ GOOD - File missing is not recoverable by retrying
raise DataError(
    code=ErrorCode.ERR_DATA_FILE_NOT_FOUND,
    message="File missing",
    recoverable=False  # No point in retrying
)
```

### 5. Use Decorators for Service Methods

```python
class MyService:
    # ✓ GOOD - Automatic error handling
    @with_error_handling(
        operation="process_data",
        component="MyService",
        fallback_value=None
    )
    def process_data(self, data):
        # ... processing ...
        pass

    # ✗ BAD - Manual try/except everywhere
    def process_data(self, data):
        try:
            # ... processing ...
            pass
        except Exception as e:
            logger.error(f"Error: {e}")
            QMessageBox.critical(None, "Error", str(e))
            return None
```

---

## Migration Strategy

### Phase 1: New Code

Use error handling in all new code:

```python
# New service method
@with_error_handling(
    operation="new_feature",
    component="NewService",
    fallback_value=None
)
def new_feature(self):
    pass
```

### Phase 2: High-Risk Areas

Update critical paths first:
- File I/O operations
- Network requests
- Database operations
- User-facing errors

### Phase 3: Gradual Migration

Update existing code opportunistically:
- When fixing bugs
- When adding features
- During refactoring

---

## Testing

### Unit Tests

```python
import pytest
from shared.errors import AppError, ErrorCode

def test_error_creation():
    error = AppError(
        code=ErrorCode.ERR_LEX_FILE_NOT_FOUND,
        message="Test error",
        user_message="User-friendly message"
    )

    assert error.code == ErrorCode.ERR_LEX_FILE_NOT_FOUND
    assert error.recoverable == False
    assert "Test error" in str(error)

def test_error_handling():
    with pytest.raises(AppError) as exc_info:
        raise AppError(
            code=ErrorCode.ERR_GEM_INVALID_INPUT,
            message="Invalid input"
        )

    assert exc_info.value.code == ErrorCode.ERR_GEM_INVALID_INPUT
```

### Integration Tests

```python
@pytest.mark.integration
def test_service_error_handling():
    service = LexiconService()

    # Should return fallback value on error
    result = service.lookup_hebrew("nonexistent")
    assert result == []  # fallback_value
```

---

## Summary

The error handling system provides:

✓ **Structured errors** - Error codes, categories, severity levels
✓ **User notifications** - Friendly messages, dialogs, auto-close
✓ **Logging** - Automatic logging with context
✓ **Recovery** - Retry strategies, cache clearing
✓ **Easy to use** - Decorators, context managers, helpers

Start using it today to improve error handling across Isopgem!
