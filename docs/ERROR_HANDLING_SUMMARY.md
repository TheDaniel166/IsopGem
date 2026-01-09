# Error Handling System - Implementation Summary

## Overview

I've implemented a complete, production-ready error handling framework for Isopgem that provides structured error handling, user-friendly notifications, automatic logging, and error recovery strategies.

---

## What Was Created

### 1. Core Error Infrastructure

#### [src/shared/errors/base.py](../src/shared/errors/base.py)
- `AppError` - Base error class with rich context
- `ErrorSeverity` - Debug, Info, Warning, Error, Critical
- `ErrorCategory` - Categorization (lexicon, etymology, network, etc.)
- Convenience subclasses: `DataError`, `ServiceError`, `NetworkError`, `ValidationError`

#### [src/shared/errors/codes.py](../src/shared/errors/codes.py)
- 60+ predefined error codes organized by pillar
- User-friendly messages for each code
- Naming convention: `{PILLAR}_{COMPONENT}_{ERROR_TYPE}`

Examples:
```python
ErrorCode.ERR_LEX_FILE_NOT_FOUND
ErrorCode.ERR_GEM_CALCULATION_FAILED
ErrorCode.ERR_NET_TIMEOUT
ErrorCode.ERR_DOC_SAVE_FAILED
```

#### [src/shared/errors/handler.py](../src/shared/errors/handler.py)
- `handle_error()` - Central error handling function
- `error_boundary` - Context manager for error boundaries
- `with_error_handling` - Decorator for automatic error handling
- `ErrorContext` - Tracks operation, component, user action
- Recovery strategies (cache clearing, file reload)

#### [src/shared/errors/ui_notifier.py](../src/shared/errors/ui_notifier.py)
- `notify_error()` - Show error dialog
- `notify_warning()` - Show warning dialog
- `notify_info()` - Show info (with auto-close)
- `notify_success()` - Show success toast
- `notify_app_error()` - Show AppError with proper styling
- `ask_retry()` - Ask user to retry operation

### 2. Documentation

#### [docs/ERROR_HANDLING_GUIDE.md](ERROR_HANDLING_GUIDE.md)
- Complete usage guide with examples
- All error codes documented
- Best practices
- Migration strategy
- Testing guide

### 3. Examples

#### [examples/error_handling_example.py](../examples/error_handling_example.py)
- Before/after comparison
- Real service implementation
- Multiple usage patterns
- Runnable examples

---

## How to Use

### Quick Example

```python
from shared.errors import AppError, ErrorCode, with_error_handling

class MyService:
    @with_error_handling(
        operation="process_data",
        component="MyService",
        fallback_value=None,
        retry_count=1
    )
    def process_data(self, data):
        """Errors are automatically handled."""
        if not data:
            raise AppError(
                code=ErrorCode.ERR_VAL_REQUIRED_FIELD,
                message="Data is required",
                user_message="Please provide valid data",
                recoverable=True
            )

        # ... processing ...
        return result
```

### Three Ways to Handle Errors

#### 1. Decorator (Recommended for service methods)
```python
@with_error_handling(
    operation="lookup_word",
    component="LexiconService",
    fallback_value=[]
)
def lookup_hebrew(self, word: str):
    return self._do_lookup(word)
```

#### 2. Context Manager (For specific code blocks)
```python
with error_boundary(
    operation="load_file",
    component="DataService",
    fallback_value=None
):
    data = load_risky_file()
```

#### 3. Manual Handling (For custom logic)
```python
try:
    result = risky_operation()
except Exception as e:
    raise AppError(
        code=ErrorCode.ERR_CUSTOM,
        message="Operation failed",
        user_message="Something went wrong",
        cause=e
    )
```

---

## Key Features

### Structured Errors

```python
AppError(
    code=ErrorCode.ERR_LEX_FILE_NOT_FOUND,       # Trackable code
    message="Hebrew lexicon not found",           # Technical (logs)
    user_message="Lexicon file is missing",      # User-friendly
    details="FileNotFoundError: hebrew.json.gz",  # Technical details
    severity=ErrorSeverity.ERROR,                 # Severity level
    recoverable=False,                            # Can user retry?
    context={"language": "hebrew"}                # Additional context
)
```

### Automatic Logging

All errors are logged with rich context:
```
[LexiconService] Failed to load Hebrew lexicon
Code: ERR_LEX_FILE_NOT_FOUND
Context: {operation: "load_lexicon", language: "hebrew", user_action: "..."}
Stack trace: ...
```

### User Notifications

Errors automatically show user-friendly dialogs:
- Error severity determines icon (warning/error/critical)
- User-friendly message shown prominently
- Technical details available in expandable section
- Recoverable errors offer "Retry" button

### Error Recovery

Some errors have automatic recovery strategies:
- `ERR_LEX_CACHE_FULL` → Clear caches, ask to retry
- `ERR_DATA_FILE_CORRUPT` → Suggest reinstall
- Network errors → Mark as recoverable, allow retry

---

## Error Codes

### By Pillar

**Lexicon** (`ERR_LEX_*`):
- `ERR_LEX_FILE_NOT_FOUND` - Lexicon file missing
- `ERR_LEX_PARSE_FAILED` - Failed to parse lexicon
- `ERR_LEX_LOOKUP_FAILED` - Lookup operation failed
- `ERR_LEX_NO_RESULTS` - No results found
- `ERR_LEX_CACHE_FULL` - Cache memory full

**Gematria** (`ERR_GEM_*`):
- `ERR_GEM_INVALID_INPUT` - Invalid input text
- `ERR_GEM_CALCULATION_FAILED` - Calculation error
- `ERR_GEM_CIPHER_NOT_FOUND` - Cipher not available
- `ERR_GEM_NO_MAPPING` - Character has no mapping

**Etymology** (`ERR_ETY_*`):
- `ERR_ETY_DB_NOT_FOUND` - Etymology database missing
- `ERR_ETY_LOOKUP_FAILED` - Lookup failed
- `ERR_ETY_API_FAILED` - API request failed
- `ERR_ETY_NETWORK_TIMEOUT` - Network timeout

**Documents** (`ERR_DOC_*`):
- `ERR_DOC_NOT_FOUND` - Document not found
- `ERR_DOC_SAVE_FAILED` - Failed to save
- `ERR_DOC_LOAD_FAILED` - Failed to load
- `ERR_DOC_PARSE_FAILED` - Parse error

**Network** (`ERR_NET_*`):
- `ERR_NET_CONNECTION_FAILED` - Connection failed
- `ERR_NET_TIMEOUT` - Request timed out
- `ERR_NET_API_ERROR` - API error

Plus 40+ more codes covering all pillars!

---

## Benefits

### Before Error Handling

```python
def lookup_hebrew(self, word: str):
    # Problems:
    # - Ugly exceptions shown to user
    # - No logging
    # - No recovery
    # - Hard to debug
    return self._do_lookup(word)
```

**User sees**: `FileNotFoundError: [Errno 2] No such file or directory: '/data/lexicons/hebrew_compact.json.gz'`

### After Error Handling

```python
@with_error_handling(
    operation="lookup_hebrew",
    component="LexiconService",
    fallback_value=[]
)
def lookup_hebrew(self, word: str):
    # Benefits:
    # - User-friendly error messages
    # - Automatic logging with context
    # - Returns fallback value on error
    # - Recovery strategies applied
    return self._do_lookup(word)
```

**User sees**: "The Hebrew lexicon file is missing. Please reinstall Isopgem."
**Plus**: Detailed technical info in collapsible section, error code for support, automatic logging

---

## Integration

### Step 1: Initialize (One-Time Setup)

In your main window initialization:

```python
from shared.errors import set_main_window

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Register main window for error notifications
        set_main_window(self)
```

### Step 2: Use in Services

Add error handling to your service methods:

```python
from shared.errors import with_error_handling, AppError, ErrorCode

class LexiconService:
    @with_error_handling(
        operation="load_lexicon",
        component="LexiconService",
        fallback_value=None
    )
    def load_lexicon(self, language: str):
        if not self.lexicon_exists(language):
            raise AppError(
                code=ErrorCode.ERR_LEX_FILE_NOT_FOUND,
                message=f"Lexicon not found: {language}",
                user_message=f"The {language} lexicon is missing. Please reinstall.",
                recoverable=False
            )
        return self._load(language)
```

### Step 3: Handle in UI

UI code doesn't need try/except blocks anymore:

```python
# Before
try:
    results = self.lexicon_service.lookup_hebrew(word)
    self.display_results(results)
except Exception as e:
    QMessageBox.critical(self, "Error", str(e))

# After
results = self.lexicon_service.lookup_hebrew(word)
self.display_results(results)
# Errors are handled automatically!
```

---

## Migration Strategy

### Phase 1: New Code (Immediate)
Use error handling in all new code going forward.

### Phase 2: Critical Paths (Week 1-2)
Update high-risk areas:
- File I/O (lexicon loading, document loading)
- Network requests (Sefaria API, etymology API)
- Database operations (saves, queries)
- User-facing errors (validation, input errors)

### Phase 3: Gradual Migration (Ongoing)
Update existing code opportunistically:
- When fixing bugs
- When adding features
- During refactoring

**No need to update everything at once!** The new system works alongside existing error handling.

---

## Testing

Error handling works with your existing test infrastructure:

```python
import pytest
from shared.errors import AppError, ErrorCode

@pytest.mark.unit
def test_error_handling():
    service = MyService()

    # Should return fallback value
    result = service.method_with_error_handling()
    assert result == []  # fallback_value

@pytest.mark.integration
def test_error_notification(mocker):
    # Mock notification to verify it's called
    mock_notify = mocker.patch('shared.errors.ui_notifier.notify_error')

    service = MyService()
    service.failing_method()

    # Verify error was shown to user
    mock_notify.assert_called_once()
```

---

## Performance

**Zero overhead when no errors occur** - The decorators and context managers add negligible overhead (~microseconds).

**Minimal overhead on errors** - Structured errors are slightly more expensive than raw exceptions, but errors should be exceptional, not the normal path.

---

## Next Steps

1. **Immediate**: Start using in new code
   ```python
   @with_error_handling(...)
   def new_method(self):
       pass
   ```

2. **This Week**: Update critical paths
   - Lexicon loading
   - Etymology lookups
   - Document saves

3. **Ongoing**: Migrate gradually
   - Update when touching code
   - No rush to update everything

---

## Files Created

```
src/shared/errors/
├── __init__.py              # Public API
├── base.py                  # AppError, ErrorSeverity, ErrorCategory
├── codes.py                 # ErrorCode, user messages
├── handler.py               # handle_error(), decorators, recovery
└── ui_notifier.py           # notify_error(), notify_success(), etc.

docs/
├── ERROR_HANDLING_GUIDE.md     # Complete usage guide
└── ERROR_HANDLING_SUMMARY.md   # This file

examples/
└── error_handling_example.py   # Runnable examples
```

---

## Summary

You now have a **production-ready error handling system** with:

✅ **60+ error codes** - Trackable, consistent
✅ **Structured errors** - Rich context, technical + user messages
✅ **Auto notifications** - User-friendly dialogs
✅ **Auto logging** - Structured logs with context
✅ **Recovery strategies** - Retry, cache clearing
✅ **Three usage patterns** - Decorators, context managers, manual
✅ **Complete documentation** - Guide, examples, best practices
✅ **Easy integration** - Works with existing code
✅ **Testing support** - Works with pytest

Start using it today to dramatically improve error handling across Isopgem!
