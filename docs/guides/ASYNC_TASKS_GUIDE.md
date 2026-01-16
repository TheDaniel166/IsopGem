## Async/Background Tasks Guide

Handle long-running operations without freezing the UI.

---

## The Problem

```python
# This FREEZES the UI
def on_button_clicked(self):
    # User can't interact with UI for 30 seconds!
    results = self.enrich_all_lexicon_entries()  # Takes 30 seconds
    self.display_results(results)
```

**Problems:**
- UI frozen (can't click, type, or scroll)
- No progress indication
- Can't cancel operation
- Poor user experience

---

## The Solution

```python
from shared.async_tasks import run_in_background

# This runs in background - UI stays responsive
@run_in_background(
    task_name="Enrich Lexicon",
    on_complete=self.display_results,
    on_progress=self.update_progress_bar
)
def enrich_all_entries(self):
    # Runs in background thread
    results = self.enrich_all_lexicon_entries()
    return results

def display_results(self, results):
    # Runs on UI thread when done
    self.result_view.show(results)
```

**Benefits:**
- ✅ UI stays responsive
- ✅ Progress indication
- ✅ Can cancel operation
- ✅ Great user experience

---

## Quick Start

### Import

```python
from shared.async_tasks import (
    BackgroundTask,
    run_in_background,
    async_method,
    get_task_manager
)
```

### Pattern 1: Decorator (Recommended)

```python
class LexiconService:
    @run_in_background(
        task_name="Load Lexicon",
        on_complete=self.on_load_complete,
        on_error=self.on_load_error
    )
    def load_lexicon(self, language: str):
        """This runs in background automatically."""
        # Heavy processing here
        data = self._load_large_file(language)
        parsed = self._parse_lexicon(data)
        return parsed

    def on_load_complete(self, result):
        """This runs on UI thread."""
        self.display_lexicon(result)
        notify_success("Lexicon loaded!")

    def on_load_error(self, error):
        """This runs on UI thread."""
        notify_error(f"Failed to load lexicon: {error}")
```

### Pattern 2: Manual Task Creation

```python
def load_lexicon_clicked(self):
    """Button click handler."""
    task = BackgroundTask(
        func=self.lexicon_service.load_lexicon,
        args=("hebrew",),
        task_name="Load Hebrew Lexicon",
        on_complete=self.on_lexicon_loaded,
        on_progress=self.update_progress
    )
    task.start()

    # Save task reference to cancel later
    self.current_task = task
```

---

## Complete Example: Enrichment Service

```python
from shared.async_tasks import run_in_background
from shared.errors import AppError, ErrorCode

class EnrichmentService:
    def __init__(self, parent_widget):
        self.parent = parent_widget
        self.current_task = None

    @run_in_background(
        task_name="Enrich Lexicon",
        on_complete=lambda self, result: self.on_enrich_complete(result),
        on_progress=lambda self, current, total, msg: self.update_progress(current, total, msg)
    )
    def enrich_all_entries(self, lexicon_data):
        """
        Enrich all lexicon entries - runs in background.

        This function runs in a worker thread, so:
        - DO NOT access UI widgets directly
        - DO use signals to communicate with UI
        - DO check for cancellation
        - DO report progress
        """
        results = []
        total = len(lexicon_data)

        for i, entry in enumerate(lexicon_data):
            # Check if cancelled
            if self.current_task and self.current_task.is_cancelled():
                return None  # Exit early

            # Enrich entry
            enriched = self._enrich_entry(entry)
            results.append(enriched)

            # Report progress (safe - uses signals internally)
            self.report_progress(i + 1, total, f"Enriched: {entry.word}")

        return results

    def on_enrich_complete(self, results):
        """
        Handle completion - runs on UI thread.

        Safe to access UI widgets here.
        """
        if results is None:
            # Cancelled
            notify_warning("Enrichment cancelled")
            return

        # Update UI
        self.parent.result_list.clear()
        for result in results:
            self.parent.result_list.add_item(result)

        notify_success(f"Enriched {len(results)} entries!")

    def update_progress(self, current, total, message):
        """
        Update progress - runs on UI thread.

        Safe to access UI widgets.
        """
        progress_percent = int((current / total) * 100)
        self.parent.progress_bar.setValue(progress_percent)
        self.parent.status_label.setText(message)

    def cancel_enrichment(self):
        """Cancel the current enrichment task."""
        if self.current_task:
            self.current_task.cancel()
```

---

## Progress Reporting

### From Inside Background Function

```python
@run_in_background(
    on_progress=self.update_progress_bar
)
def process_large_dataset(self, data):
    """Background function with progress."""
    total = len(data)

    for i, item in enumerate(data):
        # Process item
        result = self._process(item)

        # Report progress
        # This is safe - uses signals internally
        progress = int((i + 1) / total * 100)
        self.report_progress(i + 1, total, f"Processing {item.name}")

    return results

def update_progress_bar(self, current, total, message):
    """UI thread callback."""
    self.progress_bar.setValue(int(current / total * 100))
    self.status_label.setText(message)
```

---

## Cancellation

### Make Task Cancellable

```python
@run_in_background(task_name="Long Operation")
def long_operation(self, data):
    """Background task that can be cancelled."""
    results = []

    for item in data:
        # CHECK FOR CANCELLATION
        if self.current_task.is_cancelled():
            logger.info("Operation cancelled by user")
            return None  # Return early

        # Process item
        result = self._process(item)
        results.append(result)

    return results
```

### Cancel from UI

```python
class MyWindow(QWidget):
    def on_start_clicked(self):
        """Start long operation."""
        self.current_task = self.service.long_operation(self.data)

        # Enable cancel button
        self.cancel_button.setEnabled(True)

    def on_cancel_clicked(self):
        """Cancel the operation."""
        if self.current_task:
            self.current_task.cancel()
            self.cancel_button.setEnabled(False)
```

---

## Error Handling Integration

Background tasks automatically integrate with error handling system:

```python
@run_in_background(
    task_name="Load Document",
    on_complete=self.on_document_loaded
)
def load_document(self, path):
    """Errors are handled automatically."""

    # Validate (will show error dialog if invalid)
    if not path.exists():
        raise AppError(
            code=ErrorCode.ERR_DOC_NOT_FOUND,
            message=f"Document not found: {path}",
            user_message="Document file does not exist",
            recoverable=False
        )

    # Load (errors caught and shown to user)
    try:
        content = path.read_text()
        return self._parse_document(content)
    except Exception as e:
        raise AppError(
            code=ErrorCode.ERR_DOC_LOAD_FAILED,
            message=f"Failed to load document: {e}",
            user_message="Failed to load document. File may be corrupted.",
            recoverable=False,
            cause=e
        )

# Errors automatically:
# - Logged with context
# - Shown to user in dialog
# - Don't crash the app
```

---

## Task Manager

Track and control all background tasks:

```python
from shared.async_tasks import get_task_manager

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.task_manager = get_task_manager()

        # Connect to task signals
        self.task_manager.task_started.connect(self.on_task_started)
        self.task_manager.task_completed.connect(self.on_task_completed)

    def on_task_started(self, task_name):
        """Task started notification."""
        self.statusBar().showMessage(f"Started: {task_name}")

    def on_task_completed(self, task_name):
        """Task completed notification."""
        self.statusBar().showMessage(f"Completed: {task_name}", 3000)

    def closeEvent(self, event):
        """Cancel all tasks on window close."""
        if self.task_manager.active_count() > 0:
            reply = QMessageBox.question(
                self,
                "Tasks Running",
                f"{self.task_manager.active_count()} tasks are still running. Cancel them?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                self.task_manager.cancel_all()
                self.task_manager.wait_for_all(timeout_ms=5000)

        event.accept()
```

---

## Common Patterns

### Pattern 1: Load Large File

```python
@run_in_background(
    task_name="Load Lexicon",
    on_complete=self.display_lexicon
)
def load_lexicon_file(self, path):
    """Load large lexicon file in background."""
    # This takes 5-10 seconds
    data = gzip.open(path).read()
    parsed = json.loads(data)
    return parsed

def display_lexicon(self, data):
    """Display on UI thread."""
    self.lexicon_view.set_data(data)
```

### Pattern 2: Network Request

```python
@run_in_background(
    task_name="Fetch Etymology",
    on_complete=self.show_etymology
)
def fetch_from_api(self, word):
    """Fetch from API in background."""
    # This takes 2-5 seconds (network)
    response = requests.get(f"https://api.example.com/etymology/{word}")
    return response.json()

def show_etymology(self, data):
    """Show result on UI thread."""
    self.etymology_panel.display(data)
```

### Pattern 3: Batch Processing

```python
@run_in_background(
    task_name="Process Documents",
    on_progress=self.update_progress
)
def process_documents(self, documents):
    """Process multiple documents in background."""
    results = []
    total = len(documents)

    for i, doc in enumerate(documents):
        # Check cancellation
        if self.current_task.is_cancelled():
            return None

        # Process
        result = self._process_document(doc)
        results.append(result)

        # Progress
        self.report_progress(i + 1, total, f"Processed: {doc.title}")

    return results
```

### Pattern 4: Database Query

```python
@run_in_background(
    task_name="Search Database",
    on_complete=self.display_results
)
def search_database(self, query):
    """Run expensive database query in background."""
    # This might take 10+ seconds
    session = get_db_session()
    results = session.query(Document).filter(
        Document.content.contains(query)
    ).all()
    return results
```

---

## Thread Safety

### ❌ DON'T: Access UI from Background Thread

```python
@run_in_background(task_name="Bad Example")
def bad_example(self):
    # ❌ WRONG - crashes the app!
    self.label.setText("Processing...")  # UI access from worker thread

    result = process_data()

    # ❌ WRONG - crashes the app!
    self.result_view.show(result)  # UI access from worker thread

    return result
```

### ✅ DO: Use Callbacks for UI Updates

```python
@run_in_background(
    task_name="Good Example",
    on_complete=self.display_result
)
def good_example(self):
    # ✅ GOOD - no UI access in background
    result = process_data()
    return result

def display_result(self, result):
    # ✅ GOOD - UI access on UI thread
    self.result_view.show(result)
```

### ✅ DO: Use Signals for Progress

```python
@run_in_background(
    on_progress=self.update_status
)
def with_progress(self, data):
    for i, item in enumerate(data):
        process(item)

        # ✅ GOOD - uses signals internally (thread-safe)
        self.report_progress(i, len(data), f"Item {i}")

def update_status(self, current, total, message):
    # ✅ GOOD - UI access on UI thread
    self.status_label.setText(message)
```

---

## Best Practices

### 1. Always Check for Cancellation

```python
@run_in_background(task_name="Long Task")
def long_task(self, data):
    for item in data:
        # Check cancellation regularly
        if self.current_task.is_cancelled():
            return None

        process(item)
```

### 2. Report Progress for Long Operations

```python
@run_in_background(on_progress=self.update_progress)
def long_task(self, data):
    for i, item in enumerate(data):
        process(item)

        # Report every 10 items
        if i % 10 == 0:
            self.report_progress(i, len(data), f"Processed {i}/{len(data)}")
```

### 3. Handle Errors Gracefully

```python
@run_in_background(
    task_name="Risky Operation",
    on_error=self.handle_error
)
def risky_operation(self):
    try:
        return dangerous_operation()
    except Exception as e:
        raise AppError(
            code=ErrorCode.ERR_SYS_UNKNOWN,
            message=f"Operation failed: {e}",
            user_message="Operation failed. Please try again.",
            cause=e
        )
```

### 4. Provide Feedback to User

```python
@run_in_background(
    task_name="Save Document",
    on_complete=lambda self, _: notify_success("Document saved!")
)
def save_document(self, doc):
    self.db.save(doc)
    return True
```

### 5. Don't Block UI Thread

```python
# ❌ BAD - blocks UI thread
def on_button_clicked(self):
    result = expensive_operation()  # Takes 30 seconds
    self.display(result)

# ✅ GOOD - runs in background
@run_in_background(on_complete=self.display)
def on_button_clicked(self):
    return expensive_operation()
```

---

## Testing

### Unit Tests

```python
import pytest
from shared.async_tasks import BackgroundTask

@pytest.mark.unit
def test_background_task():
    """Test background task execution."""
    result = None

    def on_complete(value):
        nonlocal result
        result = value

    def work():
        return 42

    task = BackgroundTask(
        func=work,
        task_name="Test Task",
        on_complete=on_complete
    )
    task.start()

    # Wait for completion
    task.thread_pool.waitForDone()

    assert result == 42
```

---

## Summary

Background tasks solve the UI freeze problem:

✅ **Non-blocking** - UI stays responsive
✅ **Progress tracking** - User sees what's happening
✅ **Cancellable** - User can cancel long operations
✅ **Error handling** - Integrates with error system
✅ **Thread-safe** - Signals for UI communication
✅ **Easy to use** - Simple decorator API

Use `@run_in_background` for any operation that takes more than 1 second!
