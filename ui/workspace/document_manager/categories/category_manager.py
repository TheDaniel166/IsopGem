class CategoryManager:
    def __init__(self):
        self.predefined_categories = [
            'Class A', 'Class B', 'Class C', 
            'Class D', 'Class E', 'Class F',
            'Notes', 'Screenshots', 
            'Astrology Charts', 'TQ Operations'
        ]
        self.custom_categories = set()
        self.document_categories = {}  # Maps document IDs to categories
        
    def add_custom_category(self, name):
        self.custom_categories.add(name)
        
    def assign_category(self, document_id, category):
        if document_id not in self.document_categories:
            self.document_categories[document_id] = set()
        self.document_categories[document_id].add(category)
        
    def get_document_categories(self, document_id):
        return self.document_categories.get(document_id, set())
        
    def get_all_categories(self):
        return self.predefined_categories + list(self.custom_categories)