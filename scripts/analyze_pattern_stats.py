
import collections
import re

def analyze_stats():
    events = []
    with open("eclipse_patterns.md", "r") as f:
        lines = f.readlines()
        
    # Skip header (4 lines)
    if len(lines) < 5:
        print("Not enough data.")
        return

    # | Date | Type | Sun Stone | Node Stone | Node | Saros Stone | Zodiac |
    # | 2024-09-18 | LUNAR | 28 | 30 | South | 83 | 25° Vir 34' |
    
    for line in lines[4:]:
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 8: continue
        
        # parts[0] is empty, 1 is Date, 2 Type, 3 Sun, 4 Node, 5 NodeName, 6 Saros, 7 Zodiac
        events.append({
            "date": parts[1],
            "type": parts[2],
            "sun_stone": int(parts[3]),
            "node_stone": int(parts[4]),
            "node_name": parts[5],
            "saros": int(parts[6])
        })
        
    print(f"Loaded {len(events)} events.\n")
    
    # 1. Stone Frequency
    sun_counts = collections.Counter(e["sun_stone"] for e in events)
    node_counts = collections.Counter(e["node_stone"] for e in events)
    saros_counts = collections.Counter(e["saros"] for e in events)
    
    print("### Top 5 Sun Stones (Aubrey Holes)")
    for k, v in sun_counts.most_common(5):
        print(f"Hole #{k}: {v} times")
        
    print("\n### Top 5 Node Stones")
    for k, v in node_counts.most_common(5):
        print(f"Hole #{k}: {v} times")
        
    print("\n### Top 5 Saros Stones")
    for k, v in saros_counts.most_common(5):
        print(f"Hole #{k}: {v} times")
        
    # 2. Pairs (Sun, Node)
    pair_counts = collections.Counter((e["sun_stone"], e["node_stone"]) for e in events)
    print("\n### Top 5 Sun/Node Pairs")
    for (s, n), v in pair_counts.most_common(5):
        print(f"Sun #{s} + Node #{n}: {v} times")
        
    # 3. Metonic Check (19 years)
    # Check if events ~19 years apart land on same stones
    print("\n### Metonic Echoes (19-Year Stacks)")
    # Group by (Sun Stone) and see if dates are ~19 years apart
    # Actually, simpler: Iterate and look ahead
    
    metonic_hits = 0
    for i, e1 in enumerate(events):
        d1 = int(e1["date"][:4])
        for e2 in events[i+1:]:
            d2 = int(e2["date"][:4])
            diff = d2 - d1
            if diff == 19:
                if e1["sun_stone"] == e2["sun_stone"]:
                    print(f"Metonic Match! {e1['date']} -> {e2['date']} (Sun #{e1['sun_stone']})")
                    metonic_hits += 1
    
    print(f"Total Metonic Matches found: {metonic_hits}")

if __name__ == "__main__":
    analyze_stats()
