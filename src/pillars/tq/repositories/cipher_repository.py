"""
Cipher Repository - The Base-27 Lookup.
Loads and provides access to the TQ cipher correspondence table from CSV data.
"""
import csv
import os
from typing import List, Optional, Dict
from ..models.cipher_token import CipherToken

class CipherRepository:
    """
    Repository for accessing the TQ Cipher Correspondence Table.
    Loads data from 'data/cipher_correspondence.csv'.
    """

    def __init__(self):
        """
          init   logic.
        
        """
        self._tokens: List[CipherToken] = []
        self._map_decimal: Dict[int, CipherToken] = {}
        self._map_letter: Dict[str, CipherToken] = {}
        self._load_data()

    def _load_data(self):
        """Loads the CSV data into memory."""
        # Locate the CSV relative to this file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.join(current_dir, "..", "data", "cipher_correspondence.csv")
        
        if not os.path.exists(data_path):
            print(f"[WARNING] Cipher data not found at {data_path}")
            return

        with open(data_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    dec_val = int(row['Decimal'])
                    trigram = row['Trigram'].strip()
                    category = row.get('Category', '').strip() or None
                    symbol = row.get('Symbol', '').strip() or None
                    letter = row.get('Letter', '').strip() or None
                    
                    token = CipherToken(
                        decimal_value=dec_val,
                        trigram=trigram,
                        category=category,
                        symbol=symbol,
                        letter=letter
                    )
                    
                    self._tokens.append(token)
                    self._map_decimal[dec_val] = token
                    if letter:
                        self._map_letter[letter.upper()] = token
                        
                except ValueError:
                    continue

    def get_all(self) -> List[CipherToken]:
        """Returns all tokens sorted by decimal value."""
        return self._tokens

    def get_by_decimal(self, value: int) -> Optional[CipherToken]:
        """Retrieves a token by its decimal value (0-26)."""
        return self._map_decimal.get(value)

    def get_by_letter(self, letter: str) -> Optional[CipherToken]:
        """Retrieves a token by its letter (Case-Insensitive)."""
        return self._map_letter.get(letter.upper())