try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    pd = None

import os
from typing import Dict, Any

class IngestionService:
    """
    The Alchemist.
    Transmutes base metals (CSV/Excel) into Gold (JSON Grid Data).
    """
    
    @staticmethod
    def ingest_file(file_path: str) -> Dict[str, Any]:
        """
        Read a file and return the JSON structure for the CorrespondenceTable.
        Structure: {"columns": [...], "data": [[...], ...]}
        """
        if not PANDAS_AVAILABLE:
            raise ImportError("The Alchemist (pandas) is missing. Cannot transmute files.")

        if not os.path.exists(file_path):
            raise FileNotFoundError(f" The scroll '{file_path}' does not exist.")
            
        ext = os.path.splitext(file_path)[1].lower()
        
        try:
            if ext == '.csv':
                df = pd.read_csv(file_path, keep_default_na=False)
            elif ext in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path, keep_default_na=False)
            else:
                raise ValueError(f"Unknown alchemical format: {ext}")
            
            # Sanitization: Ensure all data is JSON serializable
            # We use an aggressive approach because columns might be 'object' type 
            # containing mixed non-serializable objects (like Timedelta).
            
            def sanitize_value(val):
                if pd.isna(val):
                    return ""
                if isinstance(val, (int, float, bool, str)):
                    return val
                # Force string conversion for everything else (Timestamp, Timedelta, etc.)
                return str(val)

            # Apply to entire dataframe
            # Use applymap for compatibility with older pandas versions (< 2.1.0)
            df = df.applymap(sanitize_value)
            
            # Convert to Dictionary Frame
            # orient='split' gives: {"index": [..], "columns": [..], "data": [..]}
            data = df.to_dict(orient='split')
            
            return {
                "columns": data['columns'],
                "data": data['data']
            }
            
        except Exception as e:
            raise ValueError(f"Transmutation failed: {str(e)}")

    @staticmethod
    def create_empty(rows=10, cols=5) -> Dict[str, Any]:
        """Create a blank grid."""
        columns = [chr(65+i) for i in range(cols)] # A, B, C...
        data = [['' for _ in range(cols)] for _ in range(rows)]
        return {
            "columns": columns,
            "data": data
        }
