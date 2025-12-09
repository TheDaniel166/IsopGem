import sys
import os
import csv
from pathlib import Path

# Add project root to path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.append(os.path.join(project_root, "src"))

from pillars.tq.models.amun_sound import AmunSoundCalculator

def export_amun_data(output_file="amun_ditrunes.csv"):
    calc = AmunSoundCalculator()
    
    headers = [
        "Decimal", "Ternary",
        "Ch1_Pair", "Ch1_Bigram", "Ch1_Ratio", "Ch1_Interval", "Ch1_Amp",
        "Ch2_Pair", "Ch2_Bigram", "Ch2_Ratio", "Ch2_Interval", "Ch2_Freq_Hz",
        "Ch3_Pair", "Ch3_Bigram", "Ch3_Ratio", "Ch3_Interval", "Ch3_ModRate_Hz"
    ]
    
    print(f"Calculating signatures for 0-728... Output: {output_file}")
    
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        
        for i in range(729):
            res = calc.calculate_signature(i)
            meta = res['meta']
            ch = res['channels']
            
            row = [
                meta['decimal'],
                meta['ternary'],
                # Ch1
                str(ch[1]['pair']),
                ch[1]['bigram_value'],
                ch[1]['ratio'],
                ch[1]['interval'],
                ch[1].get('output_amp', 0.0), # Use get just in case
                # Ch2
                str(ch[2]['pair']),
                ch[2]['bigram_value'],
                ch[2]['ratio'],
                ch[2]['interval'],
                f"{ch[2]['output_freq']:.3f}",
                # Ch3
                str(ch[3]['pair']),
                ch[3]['bigram_value'],
                ch[3]['ratio'],
                ch[3]['interval'],
                f"{ch[3]['output_rate']:.3f}"
            ]
            writer.writerow(row)
            
    print("Export complete.")

if __name__ == "__main__":
    # Output to current directory if not specified
    export_amun_data()
