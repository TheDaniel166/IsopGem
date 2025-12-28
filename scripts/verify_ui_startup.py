#!/usr/bin/env python3
"""
UI Startup Verification Script
Iterates through all registered windows in NavigationBus and attempts to instantiate them.
This acts as a 'Smoke Test' for the UI layer to catch ImportErrors or Initialization Errors.
"""
import sys
import os
import importlib
import logging
from PyQt6.QtWidgets import QApplication, QWidget

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "../src"))

from shared.signals.navigation_bus import WINDOW_REGISTRY
from shared.services.gematria.hebrew_calculator import HebrewGematriaCalculator
from shared.services.gematria.greek_calculator import GreekGematriaCalculator
from shared.services.gematria.tq_calculator import TQGematriaCalculator

# Configure Logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger("UI_VERIFY")

def verify_windows():
    app = QApplication(sys.argv)
    
    # Mock dependencies commonly needed
    # Some windows might need specific args. We'll try to provide minimal viable args.
    # Note: WindowManager usually instantiates with specific params, but this test 
    # checks basic import and __init__ stability.
    
    mock_calculators = [
        HebrewGematriaCalculator(),
        GreekGematriaCalculator(),
        TQGematriaCalculator()
    ]
    
    results = []
    
    print("-" * 80)
    print(f"{'WINDOW KEY':<30} | {'STATUS':<10} | {'MESSAGE'}")
    print("-" * 80)
    
    for key, info in WINDOW_REGISTRY.items():
        module_name = info["module"]
        class_name = info["class"]
        
        try:
            # 1. Import
            module = importlib.import_module(module_name)
            cls = getattr(module, class_name)
            
            # 2. Instantiate
            # We try with no args first. If that fails, we might need specific mocks.
            # Gematria windows usually need 'calculators'.
            
            try:
                if "gematria_calculator" in key or "batch" in key:
                     win = cls(calculators=mock_calculators)
                else:
                    # Generic instantiation
                    # Some might fail if they require specific kw args not provided.
                    # We'll catch TypeError and try to be helpful.
                    win = cls()
                    
                # 3. Success
                results.append((key, "PASS", ""))
                try:
                    win.close()
                    win.deleteLater()
                except:
                    pass
                
            except TypeError as te:
                # If specific arguments are required, we mark as WARNING but technically 'Import Safe'
                results.append((key, "WARN", f"Init Args Needed: {te}"))
            except Exception as e:
                results.append((key, "FAIL", str(e)))
                
        except ImportError as ie:
            results.append((key, "FAIL", f"Import Error: {ie}"))
        except AttributeError as ae:
            results.append((key, "FAIL", f"Class Not Found: {ae}"))
        except Exception as e:
            results.append((key, "FAIL", f"Unknown: {e}"))

    # Print Results
    for key, status, msg in results:
        print(f"{key:<30} | {status:<10} | {msg}")
        
    print("-" * 80)
    
    # Return code
    failures = [r for r in results if r[1] == "FAIL"]
    if failures:
        print(f"\nFAILED: {len(failures)} windows failed to initialize.")
        sys.exit(1)
    else:
        print("\nSUCCESS: All windows importable and defined.")
        sys.exit(0)

if __name__ == "__main__":
    verify_windows()
