
import csv

def verify_tzolkin_sum():
    total_sum = 0
    with open('Docs/time_mechanics/Tzolkin Cycle.csv', 'r') as f:
        reader = csv.reader(f)
        row_count = 0
        for row in reader:
            if not row or not row[0].strip():
                break # Stop at blank line
            
            # Convert to ints and sum
            # Values might have spaces
            try:
                row_sum = sum(int(x.strip()) for x in row if x.strip())
                total_sum += row_sum
                row_count += 1
            except ValueError:
                continue
                
    print(f"Total Sum: {total_sum}")
    print(f"Rows processed: {row_count}")
    
    expected = 82992
    print(f"Matches Epistle 33 (82992)? {total_sum == expected}")
    if total_sum != 0:
        print(f"Divisible by 133? {total_sum % 133 == 0} ({total_sum / 133})")

if __name__ == "__main__":
    verify_tzolkin_sum()
