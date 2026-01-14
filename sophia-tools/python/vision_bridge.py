#!/usr/bin/env python3
"""
Sophia Vision Bridge
The Eye of Form.
Renders Qt widgets headlessly to capture visual artifacts and property trees.
"""

import sys
import json
import os
import importlib.util
import importlib
import inspect
from pathlib import Path
from typing import Dict, Any, List

def setup_app():
    """Setup headless Qt Application."""
    # Force offscreen platform to avoid needing X11 display
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    
    try:
        from PyQt6.QtWidgets import QApplication
        app = QApplication.instance()
        if not app:
            app = QApplication(sys.argv)
        return app
    except ImportError:
        return None

def shield_eyes():
    """
    Pre-emptive mocking of heavy/missing dependencies to allow UI inspection 
    to proceed even if the backend is incomplete.
    """
    from unittest.mock import MagicMock
    import sys
    
    # List of known heavy/forbidden deps that might crash import time
    forbidden_knowledge = [
        "sqlalchemy", 
        "sqlalchemy.orm", 
        "sqlalchemy.ext.declarative",
        "sqlalchemy.sql",
        "sqlalchemy.ext",
        "sqlalchemy.schema",
        "sqlalchemy.types",
        "pandas", 
        "numpy",
        "scipy",
        "qtawesome",
        "pyqtribbon",
        "requests",
        "matplotlib",
        "networkx",
        "PyQt6.QtWebEngineWidgets",
        "PyQt6.QtWebEngineCore",
        "PyQt6.QtPrintSupport",
        "whoosh",
        "whoosh.fields",
        "whoosh.index",
        "whoosh.qparser",
        "whoosh.analysis",
        "whoosh.query",
        "whoosh.sorting",
        "whoosh.scoring",
        "spacy"
    ]
    
    for mod_name in forbidden_knowledge:
        if mod_name in sys.modules:
            continue
            
        try:
            importlib.import_module(mod_name)
        except (ImportError, AttributeError):
            # Create a deep magic mock
            mock = MagicMock()
            mock.__version__ = "0.0.0-mock"
            mock.__path__ = []
            sys.modules[mod_name] = mock
            
            # Link to parent if submodule
            if "." in mod_name:
                parent_name, child_name = mod_name.rsplit(".", 1)
                if parent_name in sys.modules:
                    setattr(sys.modules[parent_name], child_name, mock)

    # Surgical Fix for Inheritance (Typing issue with Mock bases)
    # If we mocked sqlalchemy, declarative_base() returning a Mock instance 
    # causes subclasses (Models) to become Mock instances, which breaks typing.List[Model].
    
    class DummyBase:
        """A dummy base class for mocked models."""
        metadata = MagicMock()
        query = MagicMock()
        
        def __init__(self, **kwargs):
            pass
            
    def fake_dec_base(*args, **kwargs):
        return DummyBase

    # Apply the fix to known paths where declarative_base resides
    if 'sqlalchemy.orm' in sys.modules and isinstance(sys.modules['sqlalchemy.orm'], MagicMock):
        sys.modules['sqlalchemy.orm'].declarative_base = fake_dec_base
        
    if 'sqlalchemy.ext.declarative' in sys.modules and isinstance(sys.modules['sqlalchemy.ext.declarative'], MagicMock):
        sys.modules['sqlalchemy.ext.declarative'].declarative_base = fake_dec_base


def import_module_dynamically(workspace: Path, target_path: Path):
    """Import module using package path to support relative imports."""
    try:
        # Convert file path to module path
        # e.g. src/pillars/gematria/ui/gematria_hub.py -> src.pillars.gematria.ui.gematria_hub
        rel_path = target_path.relative_to(workspace)
        module_path = str(rel_path.with_suffix('')).replace(os.sep, '.')
        
        return importlib.import_module(module_path)
    except Exception as e:
        # Fallback to direct file import if package import fails
        try:
            full_path = str(target_path)
            module_name = target_path.stem
            spec = importlib.util.spec_from_file_location(module_name, full_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = module
                spec.loader.exec_module(module)
                return module
        except Exception as e2:
            pass
        raise e

def dump_widget_tree(widget, depth=0, max_depth=5) -> Dict[str, Any]:
    """recursively dump widget properties."""
    if depth > max_depth:
        return {"type": type(widget).__name__, "truncated": True}
        
    try:
        from PyQt6.QtWidgets import QWidget
        
        children = []
        if isinstance(widget, QWidget):
            for child in widget.children():
                if isinstance(child, QWidget):
                    children.append(dump_widget_tree(child, depth + 1, max_depth))
                    
        rect = widget.geometry()
        
        data = {
            "type": type(widget).__name__,
            "name": widget.objectName(),
            "geometry": {
                "x": rect.x(),
                "y": rect.y(),
                "width": rect.width(),
                "height": rect.height()
            },
            "visible": widget.isVisible(),
            "enabled": widget.isEnabled(),
            "styleSheet": widget.styleSheet()[:100] + "..." if len(widget.styleSheet()) > 100 else widget.styleSheet(),
            "text": widget.text() if hasattr(widget, "text") else None,
            "children": children
        }
        return data
        
    except Exception as e:
        import traceback
        return {"error": f"Exception during inspection: {e}\n{traceback.format_exc()}"}

def create_mocks() -> Dict[str, Any]:
    """Create common mocks for IsopGem architecture."""
    from unittest.mock import MagicMock
    
    mocks = {}
    
    # Mock Signal Bus / Navigation Bus
    # Usually expected to have subscribe/publish methods
    bus = MagicMock()
    bus.objectName.return_value = "MockNavigationBus"
    mocks['bus'] = bus
    
    # Mock Service Registry / Vault
    # Usually expected to have get_service or similar
    services = MagicMock()
    services.objectName.return_value = "MockServiceRegistry"
    mocks['services'] = services
    
    # Mock Geometry / Canon
    canon = MagicMock()
    canon.objectName.return_value = "MockCanonEngine"
    mocks['canon'] = canon
    
    # Mock Calculator (Generic with string strings)
    calculator = MagicMock()
    calculator.name = "MockCalculator"
    calculator.title = "MockCalculator"
    mocks['calculator'] = calculator
    
    return mocks

def instantiate_smartly(cls):
    """Attempt to instantiate a widget by satisfying its __init__ requirements."""
    from unittest.mock import MagicMock
    
    # Strategy 1: Simple instantiation (no args)
    try:
        return cls()
    except TypeError:
        pass
    except Exception:
        pass

    # Strategy 2: Simple parent injection (parent=None)
    try:
        return cls(None)
    except TypeError:
        pass
    except Exception:
        pass
        
    # Strategy 3: Inspect signature and inject mocks
    try:
        sig = inspect.signature(cls.__init__)
        
        # Remove 'self' if it's bound (which it isn't for cls.__init__ usually, 
        # but inspect.signature on a class method usually includes it? 
        # Actually cls.__init__ is a Function, first arg is self. 
        # BUT inspect.signature(cls) gives the signature of __init__ properly without self.)
        
        args = []
        kwargs = {}
        
        mocks = create_mocks()
        
        # We start from the first parameter that isn't self. 
        # inspect.signature(cls) automatically handles this.
        bound_sig = inspect.signature(cls) 
        
        for name, param in bound_sig.parameters.items():
            if param.default != inspect.Parameter.empty:
                continue # Skip optionals
            
            # Heuristic injection based on name
            name_lower = name.lower()
            
            if name_lower == 'parent':
                kwargs[name] = None
            elif 'bus' in name_lower:
                kwargs[name] = mocks['bus']
            elif 'service' in name_lower or 'registry' in name_lower or 'vault' in name_lower:
                kwargs[name] = mocks['services']
            elif 'canon' in name_lower or 'engine' in name_lower:
                kwargs[name] = mocks['canon']
            elif 'calculator' in name_lower:
                if 'calculators' in name_lower: # Plural
                    kwargs[name] = [mocks['calculator']]
                else:
                    kwargs[name] = mocks['calculator']
            else:
                # unknown required arg, provide generic mock
                # Configure it to be string-friendly just in case
                m = MagicMock(name=f"Mock_{name}")
                m.__str__.return_value = f"Mock_{name}"
                m.name = f"Mock_{name}"
                m.text = f"Mock_{name}"
                kwargs[name] = m

        return cls(*args, **kwargs)
        
    except Exception as e:
        raise RuntimeError(f"Smart instantiation failed: {e}")

def inspect_widget(workspace: Path, target_file: str, class_name: str, mode: str):
    """Instantiate and inspect/snapshot a widget."""
    
    # Add workspace to sys.path so imports work
    if str(workspace) not in sys.path:
        sys.path.insert(0, str(workspace))
        
    # Also add src to sys.path for direct imports (e.g. 'from shared import')
    src_path = workspace / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
        
    # Setup App
    app = setup_app()
    if not app:
        return {"error": "PyQt6 not installed or failed to initialize."}
    
    full_path = workspace / target_file
    if not full_path.exists():
        return {"error": f"File not found: {full_path}"}
        
    try:
        # Pre-emptive mocking
        shield_eyes()
        
        # Import module
        module = import_module_dynamically(workspace, full_path)
        
        if not hasattr(module, class_name):
            return {"error": f"Class {class_name} not found in {module.__name__}"}
            
        cls = getattr(module, class_name)
        
        # Instantiate with smart strategy
        try:
            widget = instantiate_smartly(cls)
        except Exception as e:
             return {"error": f"Failed to instantiate {class_name}: {e}"}
        
        if not widget:
             return {"error": f"Failed to instantiate {class_name} (Unknown reason)"}

        # Force layout
        widget.resize(800, 600)
        widget.show() # Virtual show
        app.processEvents()
        
        result = {}
        
        if mode == "inspect":
            result["tree"] = dump_widget_tree(widget)
            
        elif mode == "snapshot":
            # Save snapshot
            snap_dir = workspace / ".sophia_vision" / "snapshots"
            snap_dir.mkdir(parents=True, exist_ok=True)
            
            filename = f"{class_name}_{os.getpid()}.png"
            save_path = snap_dir / filename
            
            pixmap = widget.grab()
            pixmap.save(str(save_path))
            
            result["snapshot_path"] = str(save_path)
            result["resolution"] = f"{pixmap.width()}x{pixmap.height()}"
            
        return result
        
    except Exception as e:
        import traceback
        return {"error": f"Exception during inspection: {e}\n{traceback.format_exc()}"}

def main():
    if len(sys.argv) < 5:
        print(json.dumps({"error": "Usage: vision_bridge.py workspace target class mode"}))
        sys.exit(1)
        
    workspace = Path(sys.argv[1])
    target = sys.argv[2]
    class_name = sys.argv[3]
    mode = sys.argv[4] # inspect, snapshot
    
    result = inspect_widget(workspace, target, class_name, mode)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
