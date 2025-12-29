#!/usr/bin/env python3
"""
The Final Rite: Verifying the Horizon.
Orchestrates the breaking of the 7 Seals (specifically Jupiter, Mars, Sun for now)
to certify the Astrology Pillar as Professional Grade.
"""
import sys
import os

# Ensure src in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
# Ensure scripts in path to find horizon_seals
sys.path.append(os.path.dirname(__file__))

# Clean pycache to ensure no stale bytecode
import shutil
# shutil.rmtree("../src/__pycache__", ignore_errors=True)

from horizon_seals import seal_jupiter, seal_mars, seal_sun

def main():
    print("==========================================")
    print("      THE RITE OF THE HORIZON SEALS       ")
    print("==========================================")
    
    results = {}
    
    # 1. Jupiter (Performance)
    try:
        results["Jupiter"] = seal_jupiter.run_seal()
    except Exception as e:
        print(f"❌ Jupiter Crashed: {e}")
        results["Jupiter"] = False
        
    print("-" * 40)

    # 2. Mars (Resilience)
    try:
        results["Mars"] = seal_mars.run_seal()
    except Exception as e:
        print(f"❌ Mars Crashed: {e}")
        results["Mars"] = False

    print("-" * 40)

    # 3. Sun (Accuracy)
    try:
        results["Sun"] = seal_sun.run_seal()
    except Exception as e:
        print(f"❌ Sun Crashed: {e}")
        results["Sun"] = False
        
    print("==========================================")
    print("             RITE CONCLUSION              ")
    print("==========================================")
    
    all_pass = True
    for seal, passed in results.items():
        status = "BROKEN (PASS)" if passed else "INTACT (FAIL)"
        print(f"  Seal of {seal}: {status}")
        if not passed:
            all_pass = False
            
    if all_pass:
        print("\n✅ All Seals Broken. The Horizon is Open.")
        print("   The Astrology Pillar is certified Professional Grade.")
        sys.exit(0)
    else:
        print("\n❌ The Horizon remains closed. Fix the Seals.")
        sys.exit(1)

if __name__ == "__main__":
    main()
