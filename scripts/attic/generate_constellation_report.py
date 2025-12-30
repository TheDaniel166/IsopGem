#!/usr/bin/env python3
import json
import csv
import os

def main():
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    
    # Paths
    lattice_path = os.path.join(project_root, "src/pillars/mods/data/planetary_lattices.json")
    walls_dir = os.path.join(project_root, "Docs/adyton_walls")
    output_path = os.path.join(walls_dir, "walls_constellations_complete.csv")
    
    # Wall Map
    # Order: Traditional Chaldean? Or just list them.
    # Let's use the standard Adyton order: Sun, Mercury, Venus, Moon, Mars, Jupiter, Saturn
    walls = [
        ("Sun", "sun_wall.csv"),
        ("Mercury", "mercury_wall.csv"),
        ("Venus", "venus_wall.csv"),
        ("Moon", "luna_wall.csv"),
        ("Mars", "mars_wall.csv"),
        ("Jupiter", "jupiter_wall.csv"),
        ("Saturn", "saturn_wall.csv")
    ]
    
    print(f"Loading lattices from {lattice_path}")
    with open(lattice_path, 'r') as f:
        lattices = json.load(f)
        
    results = []
    
    print("Processing walls...")
    for wall_name, csv_name in walls:
        # Load Wall Values
        csv_path = os.path.join(walls_dir, csv_name)
        if not os.path.exists(csv_path):
            print(f"WARNING: Missing wall file {csv_path}")
            continue
            
        print(f"  Reading {wall_name} ({csv_name})...")
        wall_values = []
        with open(csv_path, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                wall_values.append([int(x) for x in row if x.strip()])
                
        # Get Lattice
        # Key in JSON might be "Moon" or "Luna"? Usually "Moon".
        # Let's check keys in logic if needed, but assuming "Moon" based on WallDesigner logic.
        lattice = lattices.get(wall_name)
        if not lattice:
            print(f"WARNING: No lattice found for {wall_name}")
            continue
            
        # Process 13 Constellations (IDs 0-12)
        for i in range(13):
            # Find cells
            members = []
            for r in range(8):
                for c in range(13):
                    if lattice[r][c] == i:
                        val = wall_values[r][c]
                        members.append(val)
            
            total = sum(members)
            
            # Format ID 10,11,12 as A,B,C if preferred, but user said "list all... 8 members".
            # Keeps ID as integer 0-12 for sorting.
            
            row_data = [wall_name, i] + members + [total]
            results.append(row_data)
            
    # Write Output
    print(f"Writing report to {output_path}")
    with open(output_path, 'w', newline='') as f:
        writer = csv.writer(f)
        header = ["Wall", "Constellation_ID", "Val1", "Val2", "Val3", "Val4", "Val5", "Val6", "Val7", "Val8", "Total"]
        writer.writerow(header)
        writer.writerows(results)
        
    print("Done.")

if __name__ == "__main__":
    main()
