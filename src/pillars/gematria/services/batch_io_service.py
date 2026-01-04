
"""
Batch IO Service - The Granary Guard.

Handles the ingestion of data from various file formats (CSV, Excel) 
using heavy libraries like pandas, shielding the UI from these dependencies.
"""
from typing import List, Dict, Optional
from pathlib import Path
import csv

try:
    import pandas as pd  # type: ignore
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    pd = None  # type: ignore

class BatchIOService:
    """Service for handling batch file import/export operations."""
    
    def __init__(self):
        """
          init   logic.
        
        """
        self.pandas_available = PANDAS_AVAILABLE

    def is_pandas_available(self) -> bool:
        """Check if pandas is available for advanced file formats."""
        return self.pandas_available

    def read_file(self, file_path: str) -> List[Dict[str, str]]:
        """
        Read a file and return a list of dictionaries with normalized keys.
        Supports CSV, TSV, XLSX, XLS, ODS.
        """
        path = Path(file_path)
        ext = path.suffix.lower()
        
        if ext in ['.xlsx', '.xls', '.ods']:
            return self._read_spreadsheet(file_path, ext)
        elif ext in ['.csv', '.tsv', '.txt']:
            return self._read_text_table(file_path, ext)
        else:
            raise ValueError(f"Unsupported file format: {ext}")

    def _read_spreadsheet(self, file_path: str, ext: str) -> List[Dict[str, str]]:
        """Read Excel/ODS files using pandas."""
        if not self.pandas_available or pd is None:
            if ext == '.ods':
                 raise ImportError("Install 'pandas' and 'odfpy' to harvest LibreOffice files.")
            raise ImportError("Install 'pandas' and 'openpyxl' to harvest Excel files.")
            
        try:
            if ext == '.ods':
                df = pd.read_excel(file_path, engine='odf').fillna('')
            else:
                df = pd.read_excel(file_path).fillna('')
                
            return [{str(k).lower(): str(v) for k, v in row.items()} for row in df.to_dict('records')]  # type: ignore[reportUnknownArgumentType, reportUnknownMemberType, reportUnknownVariableType]
        except ImportError as e:
             # Repackage import errors for clarity
             raise ImportError(str(e))
        except Exception as e:
            raise Exception(f"Failed to read spreadsheet: {str(e)}")

    def _read_text_table(self, file_path: str, ext: str) -> List[Dict[str, str]]:
        """Read CSV/TSV files."""
        delimiter = '\t' if ext == '.tsv' else ','
        
        # Prefer pandas if available for robustness
        if self.pandas_available and pd is not None:
            try:
                df = pd.read_csv(file_path, delimiter=delimiter).fillna('')
                return [{str(k).lower(): str(v) for k, v in row.items()} for row in df.to_dict('records')]  # type: ignore[reportUnknownArgumentType, reportUnknownMemberType, reportUnknownVariableType]
            except Exception:
                # Fallback to csv module if pandas fails on simple text
                pass
                
        # Fallback to standard library csv
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter=delimiter)
                return [{str(k).lower(): str(v) for k, v in row.items()} for row in reader]
        except Exception as e:
            raise Exception(f"Failed to read text file: {str(e)}")