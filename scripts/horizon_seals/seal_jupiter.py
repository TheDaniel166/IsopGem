"""
The Seal of Jupiter: Performance & Expansion.
Benchmarks the Astrology Engine's capacity to handle mass creation.
"""
import time
import logging
from statistics import mean, stdev

from pillars.astrology.services.openastro_service import OpenAstroService
from pillars.astrology.models.chart_models import ChartRequest, AstrologyEvent, GeoLocation
from datetime import datetime, timedelta

def run_seal():
    print("♃ Breaking the Seal of Jupiter (Performance)...")
    
    # Setup
    service = OpenAstroService()
    base_time = datetime(2000, 1, 1, 12, 0)
    base_loc = GeoLocation("Greenwich", 51.48, 0.0)
    
    # 1. Warmup
    req = ChartRequest(AstrologyEvent("Warmup", base_time, base_loc))
    service.generate_chart(req)
    
    # 2. Benchmarking (Uncached)
    # We create UNIQUE requests to bypass cache
    ITERATIONS = 50
    durations = []
    
    print(f"   Running {ITERATIONS} unique chart generations...")
    start_total = time.time()
    
    for i in range(ITERATIONS):
        t = base_time + timedelta(days=i*10) # 10 day steps
        req = ChartRequest(AstrologyEvent(f"Bench {i}", t, base_loc))
        
        t0 = time.time()
        service.generate_chart(req)
        t1 = time.time()
        durations.append(t1 - t0)
        
    total_time = time.time() - start_total
    avg_time = mean(durations)
    
    print(f"   Total Time: {total_time:.2f}s")
    print(f"   Avg per Chart: {avg_time*1000:.2f}ms")
    
    if avg_time > 0.5:
        print("❌ Jupiter Seal Broken: Too Slow (>500ms avg)")
        return False
        
    # 3. Cache Benchmark
    # We request the SAME charts again
    print(f"   Running {ITERATIONS} cached lookups...")
    cache_durations = []
    
    for i in range(ITERATIONS):
        t = base_time + timedelta(days=i*10) 
        req = ChartRequest(AstrologyEvent(f"Bench {i}", t, base_loc))
        
        t0 = time.time()
        service.generate_chart(req)
        t1 = time.time()
        cache_durations.append(t1 - t0)

    avg_cache = mean(cache_durations)
    print(f"   Avg Cache Speed: {avg_cache*1000:.4f}ms")
    
    if avg_cache > 0.01: # Should be instant (<10ms)
        print("❌ Jupiter Seal Broken: Cache too slow (>10ms)")
        return False
        
    print("✅ Jupiter Seal Passed.")
    return True
