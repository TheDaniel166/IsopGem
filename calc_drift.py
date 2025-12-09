
import sys
import math

def verify_drift():
    # Real Physics
    earth_p = 365.256
    venus_p = 224.701
    
    # 8 Earth Years
    duration = 8.0 * earth_p
    
    # Orbits completed
    earth_orbits = duration / earth_p
    venus_orbits = duration / venus_p # 13.0039...
    
    # Degrees travelled
    e_deg = earth_orbits * 360
    v_deg = venus_orbits * 360
    
    # Venus position relative to Earth-Sun line
    # Remainder from perfect conjunction
    v_rem = v_deg % 360
    
    # Ideal would be 0 (perfect alignment)
    drift = v_rem 
    
    print(f"Duration: 8.0 Earth Years ({duration:.2f} days)")
    print(f"Venus Orbits: {venus_orbits:.5f}")
    print(f"Venus Drift: {drift:.4f} degrees")
    
    # Expected drift is approx -2.4 degrees per 8 year cycle (retrograde shift)
    # 13 * 360 = 4680
    # Actual V deg = 13.004 * 360 = 4681.44
    # Wait, 13 * 224.701 = 2921.1
    # 8 * 365.256 = 2922.0
    # Venus completes 13 orbits BEFORE Earth completes 8.
    # So when Earth hits 8 years, Venus has done 13 orbits + extra.
    # Extra = 0.9 days of movement.
    # Venus moves ~1.6 deg/day.
    # So drift should be approx +1.5 degrees? 
    # Let's check the code output.
    
    return True

if __name__ == "__main__":
    verify_drift()
