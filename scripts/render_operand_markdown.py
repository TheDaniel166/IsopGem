#!/usr/bin/env python3
"""
The Rite of Rendering (render_operand_markdown.py)
--------------------------------------------------
Generates a Markdown Table of the Operand Matrix (K = Delta / 26).
Also analyzes the Sum-9 Pattern in detail.
"""
import csv
import sys
from pathlib import Path

def render():
    input_path = Path("Docs/time_mechanics/Converse_Menorah_Deltas.csv")
    
    operands_grid = []
    
    with open(input_path, 'r') as f:
        reader = csv.reader(f)
        try:
            next(reader) # header
        except StopIteration:
            pass
        for row in reader:
            if row:
                operands_grid.append([int(int(x)/26) for x in row])
                
    # Generate Markdown Table
    print("| Row | Tone 1/2 | Tone 3/4 | Tone 5/6 | Tone 7 (Axis) | Tone 8/9 | Tone 10/11 | Tone 12/13 | Sum |")
    print("| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |")
    
    for i, row in enumerate(operands_grid):
        # Format Row
        row_str = " | ".join([str(x) for x in row])
        row_sum = sum(row)
        print(f"| **{i+1}** | {row_str} | **{row_sum}** |")
        
    print("\n\n### The Ennead Analysis (Outer Shell Sums)")
    print("| Row | Left (T1) | Right (T13) | Sum | Status |")
    print("| :--- | :---: | :---: | :---: | :--- |")
    
    for i, row in enumerate(operands_grid):
        left = row[0]
        right = row[6]
        s = left + right
        status = "🦁 THE ENNEAD" if s == 9 else ""
        print(f"| {i+1} | {left} | {right} | **{s}** | {status} |")

if __name__ == "__main__":
    render()
