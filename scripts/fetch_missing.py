
import urllib.request
import urllib.parse
from pathlib import Path

LEXICON_DIR = Path("data/lexicons").resolve()
LEXICON_DIR.mkdir(parents=True, exist_ok=True)

# Exact URLs provided by the Magus
DIRECT_URLS = [
    ("Classical Syriac", "https://kaikki.org/dictionary/Classical%20Syriac/kaikki.org-dictionary-ClassicalSyriac.jsonl"),
    ("Proto-Slavic", "https://kaikki.org/dictionary/Proto-Slavic/kaikki.org-dictionary-ProtoSlavic.jsonl"),
    ("Proto-Celtic", "https://kaikki.org/dictionary/Proto-Celtic/kaikki.org-dictionary-ProtoCeltic.jsonl")
]

def download_direct():
    print(f"Target Directory: {LEXICON_DIR}")
    
    for name, url in DIRECT_URLS:
        print(f"--- Processing {name} ---")
        
        # Determine filename from URL
        filename = url.split("/")[-1]
        target_file = LEXICON_DIR / filename
        
        if target_file.exists():
            print(f"✓ Already exists: {filename}")
            continue

        print(f"Downloading from: {url}")
        try:
            req = urllib.request.Request(url, method='HEAD')
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status == 200:
                    print(f"  -> File confirmed. Downloading...")
                    urllib.request.urlretrieve(url, target_file)
                    print(f"  ✓ Saved to {filename}")
                else:
                    print(f"  ✗ Status {response.status} for {url}")
        except Exception as e:
            print(f"  ✗ Failed: {e}")

if __name__ == "__main__":
    download_direct()
