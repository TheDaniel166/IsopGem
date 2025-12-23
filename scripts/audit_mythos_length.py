import re
import os

def audit_mythos_length(file_path):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Regex to find each constellation block
    # We look for "### Planet #ID: Name"
    # Then we capture everything until the next "###" or End of File
    constellation_pattern = re.compile(r"### (\w+) #(\d+): (.+?)\n(.*?)((?=###)|$)", re.DOTALL)
    
    matches = constellation_pattern.findall(content)
    
    under_count = 0
    total_count = 0
    
    print(f"{'Planet':<10} | {'ID':<3} | {'Name':<30} | {'Word Count':<10} | {'Status'}")
    print("-" * 80)

    for planet, cid, name, body, _ in matches:
        # Extract Mythos content
        # Look for **Mythos:** ... until **The Texture
        mythos_match = re.search(r"\*\*Mythos:\*\*(.*?)\*\*The Texture", body, re.DOTALL)
        
        if not mythos_match:
            # Fallback: maybe it ends with **The Mantra or just end of string if Texture is missing (unlikely)
            mythos_match = re.search(r"\*\*Mythos:\*\*(.*)", body, re.DOTALL)
        
        if mythos_match:
            mythos_text = mythos_match.group(1).strip()
            # Clean up markdown
            clean_text = mythos_text.replace('\n', ' ').replace('  ', ' ')
            words = clean_text.split()
            word_count = len(words)
            
            status = "OK"
            if word_count < 200:
                status = "FAIL"
                under_count += 1
                color_code = "\033[91m" # Red
                reset_code = "\033[0m"
                print(f"{color_code}{planet:<10} | {cid:<3} | {name.strip():<30} | {word_count:<10} | {status}{reset_code}")
            else:
                pass 
                # print(f"{planet:<10} | {cid:<3} | {name.strip():<30} | {word_count:<10} | {status}")
            
            total_count += 1

    print("-" * 80)
    print(f"Total Constellations Found: {total_count}")
    print(f"Under 200 Words: {under_count}")

if __name__ == "__main__":
    audit_mythos_length("Docs/adyton_walls/The_Book_of_91_Stars.md")
