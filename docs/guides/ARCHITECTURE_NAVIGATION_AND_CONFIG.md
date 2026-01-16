# Navigation Bus + Config: How They Work Together

## Overview

Isopgem uses **two complementary systems** for coordination:

1. **Navigation Bus** (`shared/signals/navigation_bus.py`) - "The Telephone"
   - Handles window-to-window communication
   - Lazy loading of window classes
   - Prevents circular imports

2. **Application Config** (`shared/config.py`) - "The Phonebook"
   - Centralized resource locations
   - Memory management settings
   - Feature flags
   - Environment detection

These work together to create a clean, decoupled architecture.

---

## The Two-Layer System

```
┌──────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                      │
│                                                           │
│  ┌──────────────┐     Navigation Bus     ┌─────────────┐│
│  │  Window A    │◄───────────────────────│  Window B   ││
│  │  (Gematria)  │  "calculation_done"    │  (Corresp)  ││
│  └──────────────┘         signals         └─────────────┘│
│         │                                         │       │
│         │ Need resource paths?      Need paths?  │       │
│         ▼                                         ▼       │
│  ┌────────────────────────────────────────────────────┐ │
│  │            Application Config                      │ │
│  │  "Where's lexicon?" → /data/lexicons              │ │
│  │  "Max memory?"      → 100 MB                      │ │
│  │  "Enable web?"      → True                        │ │
│  └────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────┘
```

---

## Real-World Example: Etymology Lookup

### User Action
User selects word "λόγος" in RTF editor and clicks "Word Origin"

### Step 1: Navigation Bus Opens Dialog

**RichTextEditor** uses navigation bus (though not strictly necessary for modeless dialogs):

```python
from shared.signals import navigation_bus

# Could emit signal for window management
# But for etymology, we directly create dialog (modeless)
def research_selection(self):
    word = self.get_selected_word()
    self._do_research(word)
```

### Step 2: Etymology Service Uses Config

**EtymologyService** now uses config for paths and features:

```python
from shared.config import get_config

class EtymologyService:
    def __init__(self):
        # Get config singleton
        config = get_config()

        # BEFORE: Brittle hardcoded path
        # self._etymology_db_path = Path(__file__).resolve().parents[4] / "data" / "etymology_db"

        # AFTER: Clean config-based path
        self._etymology_db_path = config.paths.etymology_db / "etymology.csv.gz"

        # Check feature flags
        self._enable_web_fallback = config.features.enable_etymology_web_fallback
        self._enable_wiktionary = config.features.enable_wiktionary_scraping

    def get_word_origin(self, word):
        # ... offline lookups first ...

        # Only use web if enabled
        if self._enable_web_fallback:
            result = self._try_online_api(word)
            if result:
                return result

        return empty_result()
```

### Step 3: Results Display

**ResearchDialog** shows results (no config needed - pure UI)

---

## Example: Cross-Pillar Navigation

### Scenario
User calculates gematria value in **Gematria Window** and wants to see correspondences.

### Step 1: Gematria Window Calculates

```python
from shared.signals import navigation_bus

class GematriaCalculatorWindow:
    def on_calculate(self):
        # Do calculation
        result = self.calculator.calculate("שלום")

        # Emit signal - any window can listen
        navigation_bus.lexicon_updated.emit(
            key_id=0,  # No specific key
            word="שלום"
        )

        # User clicks "Show Correspondences"
        self.on_show_correspondences(result)

    def on_show_correspondences(self, result):
        # Use navigation bus to open correspondence window
        navigation_bus.request_window.emit("emerald_tablet", {
            "value": result.value,
            "cipher": result.cipher_name,
            "word": result.word
        })
```

### Step 2: Window Manager Handles Request

**WindowManager** (subscribed to `request_window` signal):

```python
from shared.signals import navigation_bus, WINDOW_REGISTRY

class WindowManager:
    def __init__(self):
        # Subscribe to navigation bus
        navigation_bus.request_window.connect(self.handle_window_request)

    def handle_window_request(self, window_key, params):
        # Lazy import based on registry
        window_info = WINDOW_REGISTRY[window_key]
        module = importlib.import_module(window_info["module"])
        WindowClass = getattr(module, window_info["class"])

        # Create window
        window = WindowClass(parent=self.main_window, **params)
        window.show()
```

### Step 3: Correspondence Window Uses Config

**CorrespondenceHub** uses config for data:

```python
from shared.config import get_config

class CorrespondenceHub:
    def __init__(self, parent=None, value=None, cipher=None, word=None):
        super().__init__(parent)

        # Get config for data paths
        config = get_config()

        # Load correspondence data from config path
        self.data_service = CorrespondenceService(
            data_dir=config.paths.correspondences
        )

        # If value provided, show matches
        if value is not None:
            self.show_value_matches(value, cipher, word)
```

---

## Configuration in Different Environments

### Development
```python
# Config automatically detects dev environment
config = get_config()
assert not config.is_frozen
assert config.paths.data_root == Path("/home/you/projects/isopgem/data")
assert config.features.enable_performance_logging == True  # Can enable for debugging
```

### Production (Frozen)
```python
# Config automatically detects frozen environment
config = get_config()
assert config.is_frozen
assert config.paths.data_root == Path("C:/Program Files/Isopgem/data")
assert config.features.enable_performance_logging == False  # Disabled in production
```

### Testing
```python
from shared.config import reset_config, get_config
import os

def test_etymology_service():
    # Reset config and set test environment
    reset_config()
    os.environ["ISOPGEM_ETY_WEB"] = "0"  # Disable web fallback

    config = get_config()
    assert not config.features.enable_etymology_web_fallback

    # Test that service respects config
    service = EtymologyService()
    # Web lookups will be skipped
```

---

## When to Use Which System

### Use Navigation Bus When:
- ✓ Opening windows from other windows
- ✓ Broadcasting events (calculation_done, document_opened)
- ✓ Sending data between pillars
- ✓ Avoiding circular imports

**Example**: "When user finishes calculation, notify other windows"

### Use Config When:
- ✓ Getting file/directory paths
- ✓ Checking memory limits
- ✓ Checking feature flags
- ✓ Environment-specific settings

**Example**: "Where is the lexicon data stored?"

### Use Both When:
- ✓ Window A signals Window B (navigation bus)
- ✓ Both windows need data paths (config)

**Example**: "Gematria window tells Correspondence window to open, both need data"

---

## Benefits of This Architecture

### Before (Without Config)

**Etymology Service**:
```python
# Brittle - breaks if you move files
self._etymology_db_path = Path(__file__).resolve().parents[4] / "data" / "etymology_db"

# No way to disable web fallback
result = self._try_online_api(word)  # Always calls
```

**Problems**:
- Move `etymology_service.py` → breaks
- Deploy to production → wrong paths
- Want to disable web → have to edit code
- Test without network → have to mock requests

### After (With Config)

**Etymology Service**:
```python
config = get_config()

# Clean - always correct
self._etymology_db_path = config.paths.etymology_db / "etymology.csv.gz"

# Respects feature flag
if config.features.enable_etymology_web_fallback:
    result = self._try_online_api(word)
```

**Benefits**:
- Move files → update config once
- Production → config auto-detects paths
- Disable web → `export ISOPGEM_ETY_WEB=0`
- Test → reset config with mock

---

## Best Practices

### 1. Services Use Config for Resources

```python
# ✓ GOOD
class LexiconService:
    def __init__(self):
        config = get_config()
        self.data_dir = config.paths.lexicons

# ✗ BAD
class LexiconService:
    def __init__(self):
        self.data_dir = Path(__file__).parent.parent.parent / "data"
```

### 2. Windows Use Navigation Bus for Communication

```python
# ✓ GOOD
from shared.signals import navigation_bus

def open_correspondence_window(value):
    navigation_bus.request_window.emit("emerald_tablet", {"value": value})

# ✗ BAD
from pillars.correspondences.ui.correspondence_hub import CorrespondenceHub

def open_correspondence_window(value):
    window = CorrespondenceHub(value=value)  # Direct import breaks sovereignty
    window.show()
```

### 3. Config for Features, Preferences for User Choices

```python
# Config - system settings
config = get_config()
if config.features.enable_multi_language_gematria:
    scanner = LanguageScanner()

# Preferences - user choices
prefs = CipherPreferencesManager()
cipher = prefs.get_preference(Language.HEBREW)
```

---

## Migration Strategy

We've started migrating services to use config. Current status:

### ✓ Migrated
- `etymology_service.py` - Uses `config.paths.etymology_db`

### 🔄 In Progress
- `lexicon_resolver.py` - Should use `config.paths.lexicons`
- `comprehensive_lexicon_service.py` - Should use config paths

### ⏳ To Do
- All services with `Path(__file__).parents[N]` patterns
- Add config checks in WindowManager
- Add config dump to help/about dialog

---

## Environment Variables

You can override config via environment variables:

```bash
# Max lexicon cache size
export ISOPGEM_MAX_CACHE_MB=200

# Disable web fallback
export ISOPGEM_ETY_WEB=0

# Enable debug mode
export ISOPGEM_DEBUG=1

# Enable performance logging
export ISOPGEM_PERF_LOG=1
```

Then start app:
```bash
python3 main.py
```

Config will automatically load these values.

---

## Summary

**Navigation Bus** = Communication between components
**Config** = Resource locations and system settings

Together they create:
- ✓ Clean separation of concerns
- ✓ No hardcoded paths
- ✓ Easy testing
- ✓ Easy deployment
- ✓ Feature flags
- ✓ Environment detection
- ✓ No circular imports

Your navigation bus is excellent. Config complements it perfectly.
