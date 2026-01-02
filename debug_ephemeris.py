
import sys
import os
import time

# Adjust path BEFORE importing shared modules
current_dir = os.getcwd()
src_dir = os.path.join(current_dir, "src")
if src_dir not in sys.path:
    sys.path.append(src_dir)

print(f"Added {src_dir} to sys.path")

from shared.services.ephemeris_provider import EphemerisProvider

def test_load():
    print("Initializing EphemerisProvider...")
    try:
        provider = EphemerisProvider.get_instance()
    except Exception as e:
        print(f"Failed to get instance: {e}")
        return

    print("Waiting for load...")
    max_wait = 10
    for i in range(max_wait):
        if provider.is_loaded():
            print("LOADED SUCCESSFULLY!")
            return
        print(f"Waiting... {i+1}/{max_wait}")
        time.sleep(1)
        
    print("Timed out waiting for ephemeris load.")
    print("Checking thread status...")
    if provider._loading_thread.is_alive():
        print("Loading thread is still running.")
    else:
        print("Loading thread has terminated (possibly crashed).")

if __name__ == "__main__":
    test_load()
