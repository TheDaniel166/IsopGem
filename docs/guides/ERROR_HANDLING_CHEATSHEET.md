# Error Handling Cheat Sheet

Quick reference for using the error handling system.

---

## Import

```python
from shared.errors import (
    AppError, ErrorCode, ErrorSeverity,
    with_error_handling, error_boundary, handle_error,
    notify_error, notify_warning, notify_success
)
```

---

## Raise Errors

```python
# Basic
raise AppError(
    code=ErrorCode.ERR_LEX_FILE_NOT_FOUND,
    message="Lexicon not found",
    user_message="Lexicon file is missing. Please reinstall."
)

# With full context
raise AppError(
    code=ErrorCode.ERR_GEM_CALCULATION_FAILED,
    message="Calculation failed for input",
    user_message="Failed to calculate gematria value",
    details="ZeroDivisionError at line 42",
    severity=ErrorSeverity.ERROR,
    recoverable=True,
    context={"word": "שלום", "cipher": "Standard"}
)
```

---

## Decorator Pattern

```python
@with_error_handling(
    operation="method_name",
    component="ServiceName",
    fallback_value=None,  # Return this on error
    retry_count=1  # Allow 1 retry
)
def my_method(self, param):
    # Errors handled automatically
    return do_something(param)
```

---

## Context Manager Pattern

```python
with error_boundary(
    operation="load_file",
    component="FileService",
    fallback_value=[],
    notify_user=True
):
    data = load_risky_file()
    # Errors handled within this block
```

---

## Manual Pattern

```python
try:
    result = risky_operation()
except FileNotFoundError as e:
    raise AppError(
        code=ErrorCode.ERR_DATA_FILE_NOT_FOUND,
        message=f"File not found: {e}",
        user_message="Required file is missing",
        cause=e
    )
```

---

## User Notifications

```python
# Error (red X icon)
notify_error("Something went wrong", details="Error details")

# Warning (yellow triangle)
notify_warning("Cache is getting full")

# Success (auto-closes)
notify_success("Document saved", timeout_ms=2000)

# Info
notify_info("Processing complete")

# Ask retry
if ask_retry("Operation failed. Try again?"):
    retry_operation()
```

---

## Common Error Codes

### Lexicon
- `ERR_LEX_FILE_NOT_FOUND`
- `ERR_LEX_LOOKUP_FAILED`
- `ERR_LEX_CACHE_FULL`

### Gematria
- `ERR_GEM_INVALID_INPUT`
- `ERR_GEM_CALCULATION_FAILED`
- `ERR_GEM_CIPHER_NOT_FOUND`

### Documents
- `ERR_DOC_NOT_FOUND`
- `ERR_DOC_SAVE_FAILED`
- `ERR_DOC_LOAD_FAILED`

### Network
- `ERR_NET_TIMEOUT`
- `ERR_NET_CONNECTION_FAILED`
- `ERR_NET_API_ERROR`

### Validation
- `ERR_VAL_REQUIRED_FIELD`
- `ERR_VAL_INVALID_FORMAT`
- `ERR_VAL_OUT_OF_RANGE`

[See codes.py for full list]

---

## Complete Service Example

```python
from shared.errors import AppError, ErrorCode, with_error_handling

class LexiconService:
    @with_error_handling(
        operation="lookup_word",
        component="LexiconService",
        fallback_value=[]
    )
    def lookup_hebrew(self, word: str):
        # Validate
        if not word:
            raise AppError(
                code=ErrorCode.ERR_VAL_REQUIRED_FIELD,
                message="Word is required",
                user_message="Please enter a word",
                recoverable=True
            )

        # Check file exists
        if not self.lexicon_file.exists():
            raise AppError(
                code=ErrorCode.ERR_LEX_FILE_NOT_FOUND,
                message="Hebrew lexicon not found",
                user_message="Lexicon file is missing. Please reinstall.",
                recoverable=False,
                context={"language": "hebrew"}
            )

        # Perform lookup
        results = self._do_lookup(word)

        if not results:
            # This is OK - just no results
            logger.info(f"No results for: {word}")

        return results
```

---

## One-Time Setup

In your main window:

```python
from shared.errors import set_main_window

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        set_main_window(self)  # Enable notifications
```

---

## Testing

```python
import pytest
from shared.errors import AppError, ErrorCode

def test_error_handling():
    service = MyService()

    # Should return fallback value
    result = service.method_with_errors()
    assert result == []  # fallback

def test_error_raised():
    service = MyService()

    with pytest.raises(AppError) as exc:
        service.failing_method()

    assert exc.value.code == ErrorCode.ERR_SOMETHING
```

---

## Best Practices

✓ **Use specific error codes** - `ERR_LEX_FILE_NOT_FOUND` not `ERR_SYS_UNKNOWN`
✓ **Provide user-friendly messages** - "Lexicon missing" not "FileNotFoundError"
✓ **Add context** - `{"language": "hebrew", "file": "..."}` helps debugging
✓ **Mark recoverable errors** - Network errors are recoverable, file not found isn't
✓ **Use decorators for services** - Cleaner than try/except everywhere

✗ **Don't catch generic Exception** - Use specific errors
✗ **Don't show technical details to users** - Use `user_message` field
✗ **Don't mark everything recoverable** - Only if retry might work

---

## Quick Decision Tree

**Should I raise AppError?**
- File operation → `ERR_DATA_*` or `ERR_LEX_FILE_NOT_FOUND`
- Network request → `ERR_NET_*` or `ERR_ETY_API_FAILED`
- User input → `ERR_VAL_*` (mark recoverable=True)
- Calculation → `ERR_GEM_*` or `ERR_GEO_*`
- Database → `ERR_DB_*` or `ERR_DOC_*`

**Which pattern to use?**
- Service method → `@with_error_handling` decorator
- Specific block → `with error_boundary()` context manager
- Need custom logic → Manual `try/except` with `raise AppError`

**Should it be recoverable?**
- User can fix (invalid input) → `recoverable=True`
- Network/temporary error → `recoverable=True`
- File missing/corrupted → `recoverable=False`
- Programming error → `recoverable=False`

---

## Full Example

```python
from shared.errors import (
    AppError, ErrorCode, with_error_handling, notify_success
)

class DocumentService:
    @with_error_handling(
        operation="save_document",
        component="DocumentService",
        fallback_value=False,  # Return False on error
        retry_count=1
    )
    def save_document(self, doc) -> bool:
        # Validate
        if not doc.title:
            raise AppError(
                code=ErrorCode.ERR_VAL_REQUIRED_FIELD,
                message="Document title required",
                user_message="Please provide a document title",
                recoverable=True
            )

        # Save
        try:
            path = self.get_save_path(doc)
            path.write_text(doc.content)
        except PermissionError as e:
            raise AppError(
                code=ErrorCode.ERR_SYS_PERMISSION_DENIED,
                message=f"Permission denied: {path}",
                user_message="Cannot save file. Check permissions.",
                recoverable=False,
                cause=e,
                context={"path": str(path)}
            )

        # Success notification
        notify_success(f"Saved {doc.title}")
        return True
```

**User experience:**
- Invalid input → Warning dialog, can fix and retry
- Permission error → Error dialog, cannot retry
- Success → Green toast notification, auto-closes
- All errors logged automatically with context

---

## See Also

- [ERROR_HANDLING_GUIDE.md](ERROR_HANDLING_GUIDE.md) - Complete guide
- [ERROR_HANDLING_SUMMARY.md](ERROR_HANDLING_SUMMARY.md) - Implementation details
- [examples/error_handling_example.py](../examples/error_handling_example.py) - Code examples
- [src/shared/errors/codes.py](../src/shared/errors/codes.py) - All error codes
