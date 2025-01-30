class CustomCipher:
    def __init__(self, name, description=""):
        self.name = name
        self.description = description
        self.case_sensitive = True
        
        # Track which scripts are active
        self.active_scripts = {
            'english': False,
            'greek': False,
            'hebrew': False
        }
        
        # Initialize mappings for different scripts
        self.english_values = {}  # A-Z and a-z
        self.greek_values = {}    # Α-Ω and α-ω
        self.hebrew_values = {}   # א-ת
        self.hebrew_finals = {}   # ך ם ן ף ץ
        
        # Initialize default values
        self._init_empty_mappings()
    
    def _init_empty_mappings(self):
        # English (A-Z and a-z)
        for c in range(65, 91):  # A-Z
            self.english_values[chr(c)] = 0
        for c in range(97, 123):  # a-z
            self.english_values[chr(c)] = 0
            
        # Greek
        greek_upper = 'ΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩ'
        greek_lower = 'αβγδεζηθικλμνξοπρστυφχψω'
        for char in greek_upper + greek_lower:
            self.greek_values[char] = 0
            
        # Hebrew regular
        hebrew_chars = 'אבגדהוזחטיכלמנסעפצקרשת'
        for char in hebrew_chars:
            self.hebrew_values[char] = 0
            
        # Hebrew finals
        hebrew_finals = 'ךםןףץ'
        for char in hebrew_finals:
            self.hebrew_finals[char] = 0
    
    def set_value(self, char, value):
        """Set value for a character"""
        if char in self.english_values:
            self.english_values[char] = value
            if not self.case_sensitive:
                # Set same value for opposite case
                opposite = char.lower() if char.isupper() else char.upper()
                self.english_values[opposite] = value
        elif char in self.greek_values:
            self.greek_values[char] = value
            if not self.case_sensitive:
                # Set same value for opposite case
                opposite = char.lower() if char.isupper() else char.upper()
                if opposite in self.greek_values:
                    self.greek_values[opposite] = value
        elif char in self.hebrew_values:
            self.hebrew_values[char] = value
        elif char in self.hebrew_finals:
            self.hebrew_finals[char] = value
    
    def get_value(self, char):
        """Get value for a character"""
        if char in self.english_values and self.active_scripts['english']:
            return self.english_values[char]
        elif char in self.greek_values and self.active_scripts['greek']:
            return self.greek_values[char]
        elif char in self.hebrew_values and self.active_scripts['hebrew']:
            return self.hebrew_values[char]
        elif char in self.hebrew_finals and self.active_scripts['hebrew']:
            return self.hebrew_finals[char]
        return 0
    
    def set_case_sensitive(self, sensitive):
        """Toggle case sensitivity"""
        self.case_sensitive = sensitive
        if not sensitive:
            # Update all lowercase to match uppercase
            self._sync_case_values()
    
    def _sync_case_values(self):
        """Synchronize uppercase and lowercase values"""
        # English
        for c in range(65, 91):  # A-Z
            upper = chr(c)
            lower = chr(c + 32)
            value = self.english_values[upper]
            self.english_values[upper] = value
            self.english_values[lower] = value
            
        # Greek
        greek_upper = 'ΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩ'
        greek_lower = 'αβγδεζηθικλμνξοπρστυφχψω'
        for u, l in zip(greek_upper, greek_lower):
            value = self.greek_values[u]
            self.greek_values[u] = value
            self.greek_values[l] = value
    
    def to_dict(self):
        """Convert cipher to dictionary for saving"""
        # Save all non-zero values regardless of active state
        return {
            'name': self.name,
            'description': self.description,
            'case_sensitive': self.case_sensitive,
            'active_scripts': self.active_scripts,
            'english_values': {k: v for k, v in self.english_values.items() if v != 0},
            'greek_values': {k: v for k, v in self.greek_values.items() if v != 0},
            'hebrew_values': {k: v for k, v in self.hebrew_values.items() if v != 0},
            'hebrew_finals': {k: v for k, v in self.hebrew_finals.items() if v != 0}
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create cipher from dictionary"""
        cipher = cls(data['name'], data['description'])
        cipher.case_sensitive = data['case_sensitive']
        cipher.active_scripts = data['active_scripts']
        
        # Initialize empty mappings first
        cipher._init_empty_mappings()
        
        # Then update with saved values (only non-zero values were saved)
        if data.get('english_values'):
            cipher.english_values.update(data['english_values'])
        if data.get('greek_values'):
            cipher.greek_values.update(data['greek_values'])
        if data.get('hebrew_values'):
            cipher.hebrew_values.update(data['hebrew_values'])
        if data.get('hebrew_finals'):
            cipher.hebrew_finals.update(data['hebrew_finals'])
        
        return cipher 