#!/usr/bin/env python3
"""
Verification Script for Horizon Phase 4 (UX & Performance).
Tests:
1. Threaded Worker execution (Mocking Qt Event Loop)
2. Caching mechanism in OpenAstroService
3. Logging configuration
"""
import sys
import os
import time
import logging

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from PyQt6.QtCore import QCoreApplication, QThreadPool
from shared.ui.worker import BackgroundWorker
from shared.logging_config import configure_logging
from pillars.astrology.services.openastro_service import OpenAstroService
from pillars.astrology.models.chart_models import ChartRequest, AstrologyEvent, GeoLocation

# Mock global app for threads
app = QCoreApplication.instance()
if not app:
    app = QCoreApplication([])

def test_worker_function(x, y):
    time.sleep(0.5) # Simulate work
    return x + y

def run_verification():
    print("🔮 Awakening Phase 4 Engines...")
    
    # 1. Test Logging
    print("\n--- TEST 1: Logging Config ---")
    configure_logging(logging.DEBUG)
    logging.info("Validation Script Logging Test.")
    log_file = os.path.expanduser("~/.gemini/logs/gemini.log")
    if os.path.exists(log_file):
        print(f"✅ Log file created at {log_file}")
    else:
        print("❌ Log file NOT found.")

    # 2. Test Worker (Async)
    print("\n--- TEST 2: Background Worker ---")
    
    # We need an event loop to catch signals. 
    # Since this is a script, we will spin the loop briefly.
    
    params = {"result": None, "finished": False}
    
    def on_result(res):
        print(f"Worker Result: {res}")
        params["result"] = res
        
    def on_finished():
        print("Worker Finished.")
        params["finished"] = True
        app.quit() # Exit loop

    worker = BackgroundWorker(test_worker_function, 10, 20)
    worker.signals.result.connect(on_result)
    worker.signals.finished.connect(on_finished)
    
    print("Starting Worker (0.5s sleep)...")
    QThreadPool.globalInstance().start(worker)
    
    # Run loop
    app.exec()
    
    if params["result"] == 30 and params["finished"]:
        print("✅ BackgroundWorker Async execution PASS")
    else:
        print(f"❌ BackgroundWorker FAIL: {params}")

    # 3. Test Caching
    print("\n--- TEST 3: Service Caching ---")
    # We need to mock OpenAstroService._check_availability to avoid import errors if not installed
    # But usually we want to test the real class. 
    
    # We will subclass to mock the HEAVY part
    class MockService(OpenAstroService):
        def _check_availability(self): pass
        
        def _to_openastro_event(self, e): return {}
        
        def generate_chart_internal(self, request):
            time.sleep(0.2) # Simulate cost
            return "FakeResult"
            
        # We override the generate_chart method? 
        # No, we want to test the base class generate_chart logic which calls openAstro.
        # So we need to mock openAstro call inside it.
        # This is tricky without extensive mocking.
        # Alternatively, we just inspect the `_cache` dict directly after manual injection.
        
    svc = MockService()
    svc._cache["fake_key"] = "CachedResult"
    
    if "fake_key" in svc._cache:
        print("✅ Cache Dictionary functions.")
    else:
        print("❌ Cache Dictionary broken.")
        
    # We can try to hit the cache path logic if we can form a request that matches key
    # But `generate_chart` constructs key via `f"{request}"`.
    
    req = ChartRequest(AstrologyEvent("Test", time.time(), GeoLocation("Loc", 0,0)))
    key = str(req)
    svc._cache[key] = "HIT"
    
    # Now call generate_chart. If it returns "HIT", cache works.
    # Note: MockService needs to bypass `_validate_request` if we passed garbage.
    # But we passed valid-ish objects.
    
    res = svc.generate_chart(req)
    if res == "HIT":
        print("✅ OpenAstroService Cache HIT PASS")
    else:
        print(f"❌ OpenAstroService Cache MISS (Got {res})")

if __name__ == "__main__":
    run_verification()
