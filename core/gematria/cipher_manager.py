import json
import os
from pathlib import Path
from .custom_cipher import CustomCipher

class CipherManager:
    def __init__(self):
        # Create ciphers directory if it doesn't exist
        self.cipher_dir = Path("data/ciphers")
        self.cipher_dir.mkdir(parents=True, exist_ok=True)
        self.ciphers = {}  # Dictionary to store loaded ciphers
        self.load_all_ciphers()
    
    def load_all_ciphers(self):
        """Load all saved ciphers from the ciphers directory"""
        # Clear existing ciphers first
        self.ciphers.clear()
        
        # Debug print
        print("DEBUG: Loading ciphers from directory:", self.cipher_dir)
        
        for file_path in self.cipher_dir.glob("*.json"):
            try:
                print(f"DEBUG: Loading cipher from {file_path}")
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    cipher = CustomCipher.from_dict(data)
                    self.ciphers[cipher.name] = cipher
                    print(f"DEBUG: Successfully loaded cipher: {cipher.name}")
            except Exception as e:
                print(f"Error loading cipher from {file_path}: {e}")
        
        # Debug print final loaded ciphers
        print("DEBUG: Loaded ciphers:", list(self.ciphers.keys()))
    
    def save_cipher(self, cipher):
        """Save a cipher to file"""
        try:
            # Create safe filename from cipher name
            safe_name = "".join(x for x in cipher.name if x.isalnum() or x in "._- ")
            file_path = self.cipher_dir / f"{safe_name}.json"
            
            # Save to file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(cipher.to_dict(), f, ensure_ascii=False, indent=2)
            
            # Update loaded ciphers
            self.ciphers[cipher.name] = cipher
            
            print(f"DEBUG: Saved cipher {cipher.name} to {file_path}")
            return True
        except Exception as e:
            print(f"Error saving cipher {cipher.name}: {e}")
            return False
    
    def load_cipher(self, name):
        """Load a specific cipher by name"""
        return self.ciphers.get(name)
    
    def delete_cipher(self, name):
        """Delete a cipher"""
        if name in self.ciphers:
            try:
                safe_name = "".join(x for x in name if x.isalnum() or x in "._- ")
                file_path = self.cipher_dir / f"{safe_name}.json"
                if file_path.exists():
                    file_path.unlink()
                del self.ciphers[name]
                return True
            except Exception as e:
                print(f"Error deleting cipher {name}: {e}")
        return False
    
    def get_cipher_names(self):
        """Get list of all available cipher names"""
        # Use a set to avoid duplicates
        return sorted(list(set(self.ciphers.keys()))) 