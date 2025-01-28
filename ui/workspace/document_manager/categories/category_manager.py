import json
import os

class CategoryManager:
    def __init__(self):
        self.predefined_categories = [
            'Class A', 'Class B', 'Class C', 
            'Class D', 'Class E', 'Class F',
            'Notes', 'Screenshots', 
            'Astrology Charts', 'TQ Operations'
        ]
        self.custom_categories = set()
        self.config_dir = os.path.expanduser('~/.config/IsopGem')
        self.categories_file = os.path.join(self.config_dir, 'custom_categories.json')
        self.document_categories = {}  # Maps document IDs to categories
        self.load_custom_categories()

    def load_custom_categories(self):
        try:
            os.makedirs(self.config_dir, exist_ok=True)
            if os.path.exists(self.categories_file):
                with open(self.categories_file, 'r') as f:
                    self.custom_categories = set(json.load(f))
        except Exception as e:
            print(f"Error loading custom categories: {e}")
            self.custom_categories = set()

    def save_custom_categories(self):
        try:
            os.makedirs(self.config_dir, exist_ok=True)
            with open(self.categories_file, 'w') as f:
                json.dump(list(self.custom_categories), f)
        except Exception as e:
            print(f"Error saving custom categories: {e}")

    def add_custom_category(self, category):
        self.custom_categories.add(category)
        self.save_custom_categories()

    def remove_custom_category(self, category):
        self.custom_categories.remove(category)
        self.save_custom_categories()

    def assign_category(self, document_id, category):
        if document_id not in self.document_categories:
            self.document_categories[document_id] = set()
        self.document_categories[document_id].add(category)
        
    def get_document_categories(self, document_id):
        return self.document_categories.get(document_id, set())
        
    def get_all_categories(self):
        return self.predefined_categories + list(self.custom_categories)