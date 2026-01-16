
import csv

# 1. Load DNA Data
# Structure: Wall,Group,Step1_Val...Step8_Val,Seed_Coord
dna_rows = []
with open('Docs/adyton_walls/wall_seeds_dna.csv', 'r') as f:
    reader = csv.reader(f)
    header = next(reader)
    # Indices for Steps: Step1 is index 2, Step8 is index 9
    for row in reader:
        if row:
            dna_rows.append(row)

# 2. Format for Constellations File
# Structure: Wall,Constellation_ID,Val1...Val8,Total
# Note: The Constellation File seems to have variable columns or simply lists values.
# The previous file had: Wall,Constellation_ID,Val1...Val8,Total
# We will regenerate it to match this format.

formatted_rows = []
header_out = ["Wall", "Constellation_ID", "Val1", "Val2", "Val3", "Val4", "Val5", "Val6", "Val7", "Val8", "Total"]

for row in dna_rows:
    wall = row[0]
    group = row[1]
    
    # Extract Steps 1-8
    steps = [int(x) for x in row[2:10]]
    
    # Calculate Total
    total = sum(steps)
    
    new_row = [wall, group] + steps + [total]
    formatted_rows.append(new_row)

# 3. Write Output
output_file = 'Docs/adyton_walls/walls_constellations_complete.csv'
with open(output_file, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(header_out)
    writer.writerows(formatted_rows)

print(f"Successfully rectified {output_file} with {len(formatted_rows)} constellations from DNA source.")
