from pathlib import Path

class Config:
    ROOT_DIR = Path(__file__).parent.parent.parent
    RESOURCES_DIR = ROOT_DIR / 'resources'
    DOCUMENTS_DIR = ROOT_DIR / 'documents'
    DATABASE_PATH = ROOT_DIR / 'isopgem.db'
    
    @classmethod
    def get_icon(cls, name):
        return str(cls.RESOURCES_DIR / 'icons' / name) 