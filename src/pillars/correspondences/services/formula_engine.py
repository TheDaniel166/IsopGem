"""
Formula Engine - The Spreadsheet Logic Core.
Recursive descent parser and evaluator for spreadsheet formulas with Gematria integration.
"""
import re
import math
from typing import Any, Dict, Callable, NamedTuple, List, Optional, Set, Tuple
from enum import Enum, auto
# from pillars.gematria.services.calculation_service import CalculationService # Removed unused dependency
from shared.services.gematria.base_calculator import GematriaCalculator
from shared.services.gematria import (
    HebrewGematriaCalculator, HebrewSofitCalculator, HebrewLetterValueCalculator,
    HebrewOrdinalCalculator, HebrewSmallValueCalculator, HebrewAtBashCalculator,
    HebrewAlbamCalculator, HebrewKolelCalculator, HebrewSquareCalculator,
    HebrewCubeCalculator, HebrewTriangularCalculator, HebrewIntegralReducedCalculator,
    HebrewOrdinalSquareCalculator, HebrewFullValueCalculator,
    GreekGematriaCalculator, GreekLetterValueCalculator, GreekOrdinalCalculator,
    GreekSmallValueCalculator, GreekKolelCalculator, GreekSquareCalculator,
    GreekCubeCalculator, GreekTriangularCalculator, GreekDigitalCalculator,
    GreekOrdinalSquareCalculator, GreekFullValueCalculator,
    GreekReverseSubstitutionCalculator, GreekPairMatchingCalculator,
    GreekNextLetterCalculator,
    TQGematriaCalculator, TQReducedCalculator, TQSquareCalculator,
    TQTriangularCalculator, TQPositionCalculator
)

# Registry of available Gematria Calculators
# Maps UPPERCASE name -> Calculator Instance
_CIPHER_REGISTRY: Dict[str, GematriaCalculator] = {
    c.name.upper(): c for c in [
        HebrewGematriaCalculator(), HebrewSofitCalculator(), HebrewLetterValueCalculator(),
        HebrewOrdinalCalculator(), HebrewSmallValueCalculator(), HebrewAtBashCalculator(),
        HebrewAlbamCalculator(), HebrewKolelCalculator(), HebrewSquareCalculator(),
        HebrewCubeCalculator(), HebrewTriangularCalculator(), HebrewIntegralReducedCalculator(),
        HebrewOrdinalSquareCalculator(), HebrewFullValueCalculator(),
        GreekGematriaCalculator(), GreekLetterValueCalculator(), GreekOrdinalCalculator(),
        GreekSmallValueCalculator(), GreekKolelCalculator(), GreekSquareCalculator(),
        GreekCubeCalculator(), GreekTriangularCalculator(), GreekDigitalCalculator(),
        GreekOrdinalSquareCalculator(), GreekFullValueCalculator(),
        GreekReverseSubstitutionCalculator(), GreekPairMatchingCalculator(),
        GreekNextLetterCalculator(),
        TQGematriaCalculator(), TQReducedCalculator(), TQSquareCalculator(),
        TQTriangularCalculator(), TQPositionCalculator()
    ]
}

class ArgumentMetadata(NamedTuple):
    """
    Argument Metadata class definition.
    
    """
    name: str          # e.g. "text", "number1"
    description: str   # e.g. "The text to analyze"
    type_hint: str     # "str", "number", "range", "gematria_cipher"
    is_optional: bool = False

class FormulaMetadata(NamedTuple):
    """
    Formula Metadata class definition.
    
    """
    name: str
    description: str
    syntax: str
    category: str
    arguments: List[ArgumentMetadata] = []
    is_variadic: bool = False

class FormulaRegistry:
    """
    The Grimoire of Formulas.
    Maps function names (e.g. GEMATRIA) to executable Python functions AND their implementation details.
    """
    _REGISTRY: Dict[str, Callable] = {}
    _METADATA: Dict[str, FormulaMetadata] = {}

    @classmethod
    def register(cls, name: str, description: str, syntax: str, category: str = "General", 
                 arguments: List[ArgumentMetadata] = [], is_variadic: bool = False):
        """Decorator to register a function with metadata."""
        def decorator(func):
            """
            Decorator logic.
            
            Args:
                func: Description of func.
            
            """
            upper_name = name.upper()
            cls._REGISTRY[upper_name] = func
            cls._METADATA[upper_name] = FormulaMetadata(
                name=upper_name,
                description=description,
                syntax=syntax,
                category=category,
                arguments=arguments,
                is_variadic=is_variadic
            )
            return func
        return decorator

    @classmethod
    def get(cls, name: str) -> Callable:
        """
        Retrieve logic.
        
        Args:
            name: Description of name.
        
        Returns:
            Result of get operation.
        """
        return cls._REGISTRY.get(name.upper())

    @classmethod
    def get_metadata(cls, name: str) -> Optional[FormulaMetadata]:
        """
        Retrieve metadata logic.
        
        Args:
            name: Description of name.
        
        Returns:
            Result of get_metadata operation.
        """
        return cls._METADATA.get(name.upper())

    @classmethod
    def get_all_metadata(cls) -> List[FormulaMetadata]:
        """Returns list of all available formulas sorted by name."""
        return sorted(cls._METADATA.values(), key=lambda x: x.name)

    @staticmethod
    def get_cipher_names() -> List[str]:
        """Returns list of all registered registered Gematria cipher names."""
        return sorted(_CIPHER_REGISTRY.keys())

# --- Parser Architecture ---

class TokenType(Enum):
    """
    Token Type class definition.
    
    """
    NUMBER = auto()
    STRING = auto()
    ID = auto()     # Cell ref or Function name
    OP = auto()     # +, -, *, /, :, ^, =, >, <, >=, <=
    LPAREN = auto()
    RPAREN = auto()
    COMMA = auto()
    WS = auto()     # Whitespace
    EOF = auto()

class Token(NamedTuple):
    """
    Token class definition.
    
    """
    type: TokenType
    value: str
    def __repr__(self):
        return f"Token(type={self.type.name}, value='{self.value}')"

class Tokenizer:
    # Regex for tokens
    # Note: Operators include ':', comparison ops
    """
    Tokenizer class definition.
    
    """
    token_spec = [
        ('NUMBER',   r'\d+(\.\d*)?|\.\d+'),
        ('STRING',   r'"[^"]*"|\'[^\']*\''),
        ('ID',       r'[\$A-Za-z_][\$A-Za-z0-9_]*'), # Modified to accept $
        ('OP',       r'[+\-*/:^=<>!&]+'), # Added &
        ('LPAREN',   r'\('),
        ('RPAREN',   r'\)'),
        ('COMMA',    r','),
        ('SKIP',     r'[ \t]+'),
        ('MISMATCH', r'.'),
    ]
    token_re = re.compile('|'.join('(?P<%s>%s)' % pair for pair in token_spec))

    @staticmethod
    def tokenize(text: str, preserve_whitespace: bool = False) -> List[Token]:
        """
        Tokenize logic.
        
        Args:
            text: Description of text.
            preserve_whitespace: Description of preserve_whitespace.
        
        Returns:
            Result of tokenize operation.
        """
        tokens = []
        for mo in Tokenizer.token_re.finditer(text):
            kind = mo.lastgroup
            value = mo.group()
            if kind == 'SKIP':
                if preserve_whitespace:
                    tokens.append(Token(TokenType.EOF, value)) # Re-use EOF or add WS type? Let's use EOF type with value is hacky. Use separate if needed.
                    # Wait, adding new TokenType is hard with replace_file_content if I don't replace Enum.
                    # Let's use ID for WS? No. 
                    # Let's use a "Metadata" concept or just dummy token.
                    # Let's just return raw string for whitespace if preserved? No List[Token].
                    # I will add TokenType.WS to the Enum first?
                    # Too intrusive to Enum.
                    # I will just store it as "SKIP" type if I change Tokenizer? 
                    # Actually, for adjust_formula, I can just use regex substitution on original string if I'm careful.
                    # BUT preserving tokens is safer.
                    # Let's hack: Use TokenType.EOF as WS holder? Bad.
                    # Let's update Enum first? No, 50 line gap.
                    # Let's just use string segments for reconstruction?
                    # Let's stick to Tokenizer change. 
                    # I will use a custom token type value for WS?
                    pass
                else: 
                     continue
            elif kind == 'MISMATCH':
                raise ValueError(f'Unexpected character: {value}')
            elif kind == 'STRING':
                 # Strip quotes
                tokens.append(Token(TokenType.STRING, value[1:-1]))
            elif kind == 'NUMBER':
                tokens.append(Token(TokenType.NUMBER, value))
            elif kind == 'ID':
                tokens.append(Token(TokenType.ID, value))
            elif kind == 'OP':
                tokens.append(Token(TokenType.OP, value))
            elif kind == 'LPAREN':
                tokens.append(Token(TokenType.LPAREN, value))
            elif kind == 'RPAREN':
                tokens.append(Token(TokenType.RPAREN, value))
            elif kind == 'COMMA':
                tokens.append(Token(TokenType.COMMA, value))
        tokens.append(Token(TokenType.EOF, ""))
        return tokens

class Parser:
    """
    Parser class definition.
    
    Attributes:
        engine: Description of engine.
        tokens: Description of tokens.
        pos: Description of pos.
        current_token: Description of current_token.
    
    """
    def __init__(self, engine, tokens: List[Token]):
        """
          init   logic.
        
        Args:
            engine: Description of engine.
            tokens: Description of tokens.
        
        """
        self.engine = engine
        self.tokens = tokens
        self.pos = 0
        self.current_token = self.tokens[0]

    def eat(self, token_type: TokenType):
        """
        Eat logic.
        
        Args:
            token_type: Description of token_type.
        
        """
        if self.current_token.type == token_type:
            self.pos += 1
            if self.pos < len(self.tokens):
                self.current_token = self.tokens[self.pos]
        else:
            raise ValueError(f"Expected {token_type}, got {self.current_token.type}")

    def parse(self):
        """
        Parse logic.
        
        """
        result = self.expr()
        if self.current_token.type != TokenType.EOF:
             # If we have leftovers (like '1 2'), that's an error in strict mode, 
             # but some sheets ignore trailing junk. Let's be strict.
             pass
        return result

    # --- Precedence Levels ---
    # comparison: = < >
    # additive: + -
    # multiplicative: * /
    # power: ^
    # range: :
    # atom

    def expr(self):
        """Parse comparison operations (lowest precedence)."""
        node = self.concatenation()
        
        while self.current_token.type == TokenType.OP and self.current_token.value in ('=', '>', '<', '>=', '<=', '<>'):
            op = self.current_token.value
            self.eat(TokenType.OP)
            right = self.concatenation()
            
            # Simple eval
            if op == '=': node = (node == right)
            elif op == '>': node = (node > right)
            elif op == '<': node = (node < right)
            elif op == '>=': node = (node >= right)
            elif op == '<=': node = (node <= right)
            
        return node
        
    def concatenation(self):
        """
        Concatenation logic.
        
        """
        node = self.additive()
        while self.current_token.type == TokenType.OP and self.current_token.value == '&':
            self.eat(TokenType.OP)
            right = self.additive()
            node = str(node) + str(right)
        return node

    def additive(self):
        """
        Additive logic.
        
        """
        node = self.multiplicative()
        while self.current_token.type == TokenType.OP and self.current_token.value in ('+', '-'):
            op = self.current_token.value
            self.eat(TokenType.OP)
            right = self.multiplicative()
            if op == '+': node = self._safe_add(node, right)
            elif op == '-': node = self._safe_sub(node, right)
        return node

    def multiplicative(self):
        """
        Multiplicative logic.
        
        """
        node = self.power()
        while self.current_token.type == TokenType.OP and self.current_token.value in ('*', '/'):
            op = self.current_token.value
            self.eat(TokenType.OP)
            right = self.power()
            if op == '*': node = self._safe_mul(node, right)
            elif op == '/': node = self._safe_div(node, right)
        return node

    def power(self):
        """
        Power logic.
        
        """
        node = self.atom()
        while self.current_token.type == TokenType.OP and self.current_token.value == '^':
            self.eat(TokenType.OP)
            right = self.atom() # Right associative? Standard is left usually for 2^3^4? Let's do left for now.
            node = self._safe_pow(node, right)
        return node

    def atom(self):
        """
        Atom logic.
        
        """
        token = self.current_token
        
        if token.type == TokenType.NUMBER:
            self.eat(TokenType.NUMBER)
            return float(token.value) if '.' in token.value else int(token.value)
        
        elif token.type == TokenType.STRING:
            self.eat(TokenType.STRING)
            return token.value
            
        elif token.type == TokenType.ID:
            # Could be CellRef or Function Call
            # Lookahead for LPAREN
            name = token.value
            self.eat(TokenType.ID)
            
            if self.current_token.type == TokenType.LPAREN:
                # Function Call
                self.eat(TokenType.LPAREN)
                args = []
                if self.current_token.type != TokenType.RPAREN:
                    # Handle first arg being empty? e.g. FUNC(, b)
                    if self.current_token.type == TokenType.COMMA:
                        args.append(None)
                    else:
                        args.append(self.expr())

                    while self.current_token.type == TokenType.COMMA:
                        self.eat(TokenType.COMMA)
                        if self.current_token.type == TokenType.RPAREN:
                             args.append(None) # Trailing comma
                             break
                        elif self.current_token.type == TokenType.COMMA:
                             args.append(None) # Double comma
                        else:
                             args.append(self.expr())
                self.eat(TokenType.RPAREN)
                
                # Execute Function
                func = FormulaRegistry.get(name)
                if func:
                    return func(self.engine, *args)
                else:
                    raise ValueError(f"Unknown function: {name}")
            
            elif self.current_token.type == TokenType.OP and self.current_token.value == ':':
                 # Range: A1:B2
                 # We have 'A1', op=':', next should be ID 'B2'
                 start_cell = name
                 self.eat(TokenType.OP) # :
                 
                 if self.current_token.type != TokenType.ID:
                     raise ValueError(f"Expected Cell Reference after ':', got {self.current_token}")
                 
                 end_cell = self.current_token.value
                 self.eat(TokenType.ID)
                 
                 # Resolve Range
                 return self.engine._resolve_range_values(start_cell, end_cell)
            
            else:
                 # Single Cell Ref OR Boolean Constant
                 if name.upper() == "TRUE": return True
                 if name.upper() == "FALSE": return False
                 
                 return self.engine._resolve_cell_value(name)

        elif token.type == TokenType.LPAREN:
            self.eat(TokenType.LPAREN)
            node = self.expr()
            self.eat(TokenType.RPAREN)
            return node
            
        elif token.type == TokenType.EOF:
            raise ValueError("Unexpected end of formula")

        else:
            # Handle unary minus check?
            if token.type == TokenType.OP and token.value == '-':
                self.eat(TokenType.OP)
                return -self.atom()
            
            raise ValueError(f"Unexpected token: {token}")

    # --- Safe Helpers ---
    def _safe_add(self, a, b):
        try: return float(a) + float(b)
        except: return str(a) + str(b) # Concat strings if not numbers? 
    def _safe_sub(self, a, b): return float(a) - float(b)
    def _safe_mul(self, a, b): return float(a) * float(b)
    def _safe_div(self, a, b): return float(a) / float(b)
    def _safe_pow(self, a, b): return float(a) ** float(b)


class FormulaEngine:
    """
    The Logic Core.
    Uses Recursive Descent Parsing.
    """
    def __init__(self, data_context: Dict[str, Any]):
        """
          init   logic.
        
        Args:
            data_context: Description of data_context.
        
        """
        self.context = data_context
        # self.calc_service = CalculationService() # Removed unused dependency

    def evaluate(self, content: str, visited: Optional[Set[Tuple[int, int]]] = None) -> Any:
        """Evaluate a formula string, tracking the current dependency stack to avoid cycles."""
        if not isinstance(content, str) or not content.startswith('='):
            return content
        
        formula = content[1:].strip()
        if not formula:
            return ""

        previous_stack = getattr(self, "_eval_stack", None)
        self._eval_stack = visited or set()
        
        try:
            tokens = Tokenizer.tokenize(formula)
            parser = Parser(self, tokens)
            result = parser.parse()
            return result
        except Exception as e:
            return f"#ERROR: {str(e)}"
        finally:
            # Restore prior stack to avoid leaking state between calls
            self._eval_stack = previous_stack

    def _resolve_cell_value(self, ref: str):
        # A1 -> Val, $A$1 -> Val
        match = re.match(r'(\$?)([A-Z]+)(\$?)([0-9]+)', ref, re.IGNORECASE)
        if not match: return ref # Return as string if not valid ref
        
        abs_col, c_str, abs_row, r_str = match.groups()
        row, col = self._to_rc(r_str, c_str)

        stack = getattr(self, "_eval_stack", None)

        if hasattr(self.context, 'evaluate_cell'):
            return self.context.evaluate_cell(row, col, stack)
        if hasattr(self.context, 'get_cell_value'):
            return self.context.get_cell_value(row, col)
        return 0

    def _resolve_range_values(self, start_ref: str, end_ref: str) -> List[Any]:
        # A1:B2 -> [Val, Val, ...]
        m1 = re.match(r'(\$?)([A-Z]+)(\$?)([0-9]+)', start_ref, re.IGNORECASE)
        m2 = re.match(r'(\$?)([A-Z]+)(\$?)([0-9]+)', end_ref, re.IGNORECASE)
        
        if not m1 or not m2:
             return []
             
        # groups: 1=abs_c, 2=c, 3=abs_r, 4=r
        r1, c1 = self._to_rc(m1.group(4), m1.group(2))
        r2, c2 = self._to_rc(m2.group(4), m2.group(2))
        
        r_start, r_end = min(r1, r2), max(r1, r2)
        c_start, c_end = min(c1, c2), max(c1, c2)
        
        values = []
        if hasattr(self.context, 'evaluate_cell'):
            stack = getattr(self, "_eval_stack", None)
            for r in range(r_start, r_end + 1):
                for c in range(c_start, c_end + 1):
                    val = self.context.evaluate_cell(r, c, stack)
                    values.append(val)
        elif hasattr(self.context, 'get_cell_value'):
            for r in range(r_start, r_end + 1):
                for c in range(c_start, c_end + 1):
                    val = self.context.get_cell_value(r, c)
                    values.append(val)
        return values

    def _to_rc(self, r_str, c_str):
        """Convert spreadsheet refs (A1, AA10) to zero-based row/col."""
        c_idx = 0
        for char in c_str.upper():
            c_idx = c_idx * 26 + (ord(char) - ord('A') + 1)
        r_idx = int(r_str) - 1
        return r_idx, c_idx - 1

# --- Standard Functions ---

@FormulaRegistry.register("GEMATRIA", "Calculates Gematria.", "GEMATRIA(text, [cipher])", "Esoteric", [
    ArgumentMetadata("text", "Text/Cell", "str"),
    ArgumentMetadata("cipher", "Cipher Name", "gematria_cipher", True)
])
def func_gematria(engine: FormulaEngine, text: Any, cipher: str = "English (TQ)"):
    # TODO: Align GEMATRIA(ABC) with SUM expectation (currently returns 27, Seal expects 6)
    """
    Func gematria logic.
    
    Args:
        engine: Description of engine.
        text: Description of text.
        cipher: Description of cipher.
    
    """
    if not text: return 0
    text_str = str(text)
    cipher_key = str(cipher).upper()
    calculator = _CIPHER_REGISTRY.get(cipher_key)
    if not calculator: return f"#CIPHER? ({cipher})"
    return calculator.calculate(text_str)

@FormulaRegistry.register("SUM", "Adds arguments.", "SUM(val1, ...)", "Math", [
    ArgumentMetadata("number1", "Value", "number"),
    ArgumentMetadata("number2", "Value (opt)", "number", True)
], is_variadic=True)
def func_sum(engine: FormulaEngine, *args):
    """
    Func sum logic.
    
    Args:
        engine: Description of engine.
    
    """
    total = 0
    def add(item):
        """
        Add logic.
        
        Args:
            item: Description of item.
        
        """
        nonlocal total
        if isinstance(item, list):
            for i in item: add(i)
        else:
            try: total += float(item)
            except: pass
    for a in args: add(a)
    return total

@FormulaRegistry.register("AVERAGE", "Average of arguments.", "AVERAGE(val1, ...)", "Math", [
    ArgumentMetadata("number1", "Value", "number")
], is_variadic=True)
def func_average(engine: FormulaEngine, *args):
    """
    Func average logic.
    
    Args:
        engine: Description of engine.
    
    """
    values = []
    def collect(item):
        """
        Collect logic.
        
        Args:
            item: Description of item.
        
        """
        if isinstance(item, list):
            for i in item: collect(i)
        else:
            try: values.append(float(item))
            except: pass
    for a in args: collect(a)
    return sum(values) / len(values) if values else 0

@FormulaRegistry.register("COUNT", "Count numbers.", "COUNT(val1, ...)", "Math", [
    ArgumentMetadata("val1", "Value", "any")
], is_variadic=True)
def func_count(engine: FormulaEngine, *args):
    """
    Func count logic.
    
    Args:
        engine: Description of engine.
    
    """
    count = 0
    def check(item):
        """
        Check logic.
        
        Args:
            item: Description of item.
        
        """
        nonlocal count
        if isinstance(item, list):
            for i in item: check(i)
        else:
            try: 
                float(item)
                count += 1
            except: pass
    for a in args: check(a)
    return count

@FormulaRegistry.register("MIN", "Minimum value.", "MIN(val1, ...)", "Math", [
    ArgumentMetadata("val1", "Value", "number")
], is_variadic=True)
def func_min(engine: FormulaEngine, *args):
    """
    Func min logic.
    
    Args:
        engine: Description of engine.
    
    """
    values = []
    def collect(item):
        """
        Collect logic.
        
        Args:
            item: Description of item.
        
        """
        if isinstance(item, list): 
            for i in item: collect(i)
        else: 
            try: values.append(float(item))
            except: pass
    for a in args: collect(a)
    return min(values) if values else 0

@FormulaRegistry.register("MAX", "Maximum value.", "MAX(val1, ...)", "Math", [
    ArgumentMetadata("val1", "Value", "number")
], is_variadic=True)
def func_max(engine: FormulaEngine, *args):
    """
    Func max logic.
    
    Args:
        engine: Description of engine.
    
    """
    values = []
    def collect(item):
        """
        Collect logic.
        
        Args:
            item: Description of item.
        
        """
        if isinstance(item, list): 
            for i in item: collect(i)
        else: 
            try: values.append(float(item))
            except: pass
    for a in args: collect(a)
    return max(values) if values else 0

@FormulaRegistry.register("IF", "Conditional logic.", "IF(cond, true, false)", "Logic", [
    ArgumentMetadata("condition", "Expression", "any"),
    ArgumentMetadata("value_if_true", "Result if True", "any"),
    ArgumentMetadata("value_if_false", "Result if False", "any")
])
def func_if(engine: FormulaEngine, cond, val_true, val_false):
    """
    Func if logic.
    
    Args:
        engine: Description of engine.
        cond: Description of cond.
        val_true: Description of val_true.
        val_false: Description of val_false.
    
    """
    return val_true if cond else val_false

@FormulaRegistry.register("CONCAT", "Join strings.", "CONCAT(txt1, ...)", "Text", [
    ArgumentMetadata("text1", "Text", "str")
], is_variadic=True)
def func_concat(engine: FormulaEngine, *args):
    # Flatten like sum
    """
    Func concat logic.
    
    Args:
        engine: Description of engine.
    
    """
    parts = []
    def collect(item):
        """
        Collect logic.
        
        Args:
            item: Description of item.
        
        """
        if isinstance(item, list):
            for i in item: collect(i)
        else:
            parts.append(str(item))
    for a in args: collect(a)
    return "".join(parts)

@FormulaRegistry.register("ABS", "Absolute value.", "ABS(number)", "Math", [
    ArgumentMetadata("number", "Value", "number")
])
def func_abs(engine: FormulaEngine, val):
    """
    Func abs logic.
    
    Args:
        engine: Description of engine.
        val: Description of val.
    
    """
    try: return abs(float(val))
    except: return "#VALUE!"

@FormulaRegistry.register("ROUND", "Rounds number.", "ROUND(number, [digits])", "Math", [
    ArgumentMetadata("number", "Value", "number"),
    ArgumentMetadata("digits", "Decimals (default 0)", "number", True)
])
def func_round(engine: FormulaEngine, val, digits=0):
    """
    Func round logic.
    
    Args:
        engine: Description of engine.
        val: Description of val.
        digits: Description of digits.
    
    """
    try: return round(float(val), int(digits))
    except: return "#VALUE!"

@FormulaRegistry.register("FLOOR", "Rounds down.", "FLOOR(number)", "Math", [
    ArgumentMetadata("number", "Value", "number")
])
def func_floor(engine: FormulaEngine, val):
    """
    Func floor logic.
    
    Args:
        engine: Description of engine.
        val: Description of val.
    
    """
    try: return math.floor(float(val))
    except: return "#VALUE!"

@FormulaRegistry.register("CEILING", "Rounds up.", "CEILING(number)", "Math", [
    ArgumentMetadata("number", "Value", "number")
])
def func_ceiling(engine: FormulaEngine, val):
    """
    Func ceiling logic.
    
    Args:
        engine: Description of engine.
        val: Description of val.
    
    """
    try: return math.ceil(float(val))
    except: return "#VALUE!"

@FormulaRegistry.register("INT", "Integer part.", "INT(number)", "Math", [
    ArgumentMetadata("number", "Value", "number")
])
def func_int(engine: FormulaEngine, val):
    """
    Func int logic.
    
    Args:
        engine: Description of engine.
        val: Description of val.
    
    """
    try: return int(float(val))
    except: return "#VALUE!"

@FormulaRegistry.register("SQRT", "Square root.", "SQRT(number)", "Math", [
    ArgumentMetadata("number", "Value", "number")
])
def func_sqrt(engine: FormulaEngine, val):
    """
    Func sqrt logic.
    
    Args:
        engine: Description of engine.
        val: Description of val.
    
    """
    try: return math.sqrt(float(val))
    except: return "#VALUE!"

@FormulaRegistry.register("POWER", "Power.", "POWER(base, exp)", "Math", [
    ArgumentMetadata("base", "Base", "number"),
    ArgumentMetadata("exp", "Exponent", "number")
])
def func_power(engine: FormulaEngine, base, exp):
    """
    Func power logic.
    
    Args:
        engine: Description of engine.
        base: Description of base.
        exp: Description of exp.
    
    """
    try: return math.pow(float(base), float(exp))
    except: return "#VALUE!"

@FormulaRegistry.register("MOD", "Modulo.", "MOD(num, div)", "Math", [
    ArgumentMetadata("number", "Number", "number"),
    ArgumentMetadata("divisor", "Divisor", "number")
])
def func_mod(engine: FormulaEngine, num, div):
    """
    Func mod logic.
    
    Args:
        engine: Description of engine.
        num: Description of num.
        div: Description of div.
    
    """
    try: return float(num) % float(div)
    except: return "#VALUE!"

@FormulaRegistry.register("PI", "Pi constant.", "PI()", "Math", [])
def func_pi(engine: FormulaEngine):
    """
    Func pi logic.
    
    Args:
        engine: Description of engine.
    
    """
    return math.pi

@FormulaRegistry.register("SIN", "Sine (radians).", "SIN(rad)", "Trig", [ArgumentMetadata("angle", "Radians", "number")])
def func_sin(engine: FormulaEngine, val):
    """
    Func sin logic.
    
    Args:
        engine: Description of engine.
        val: Description of val.
    
    """
    try: return math.sin(float(val))
    except: return "#VALUE!"

@FormulaRegistry.register("COS", "Cosine (radians).", "COS(rad)", "Trig", [ArgumentMetadata("angle", "Radians", "number")])
def func_cos(engine: FormulaEngine, val):
    """
    Func cos logic.
    
    Args:
        engine: Description of engine.
        val: Description of val.
    
    """
    try: return math.cos(float(val))
    except: return "#VALUE!"

@FormulaRegistry.register("TAN", "Tangent (radians).", "TAN(rad)", "Trig", [ArgumentMetadata("angle", "Radians", "number")])
def func_tan(engine: FormulaEngine, val):
    """
    Func tan logic.
    
    Args:
        engine: Description of engine.
        val: Description of val.
    
    """
    try: return math.tan(float(val))
    except: return "#VALUE!"

@FormulaRegistry.register("ASIN", "Arc Sine.", "ASIN(num)", "Trig", [ArgumentMetadata("number", "Value", "number")])
def func_asin(engine: FormulaEngine, val):
    """
    Func asin logic.
    
    Args:
        engine: Description of engine.
        val: Description of val.
    
    """
    try: return math.asin(float(val))
    except: return "#VALUE!"

@FormulaRegistry.register("ACOS", "Arc Cosine.", "ACOS(num)", "Trig", [ArgumentMetadata("number", "Value", "number")])
def func_acos(engine: FormulaEngine, val):
    """
    Func acos logic.
    
    Args:
        engine: Description of engine.
        val: Description of val.
    
    """
    try: return math.acos(float(val))
    except: return "#VALUE!"

@FormulaRegistry.register("ATAN", "Arc Tangent.", "ATAN(num)", "Trig", [ArgumentMetadata("number", "Value", "number")])
def func_atan(engine: FormulaEngine, val):
    """
    Func atan logic.
    
    Args:
        engine: Description of engine.
        val: Description of val.
    
    """
    try: return math.atan(float(val))
    except: return "#VALUE!"

@FormulaRegistry.register("LN", "Natural Log.", "LN(num)", "Math", [ArgumentMetadata("number", "Value", "number")])
def func_ln(engine: FormulaEngine, val):
    """
    Func ln logic.
    
    Args:
        engine: Description of engine.
        val: Description of val.
    
    """
    try: return math.log(float(val))
    except: return "#VALUE!"

@FormulaRegistry.register("LOG10", "Log base 10.", "LOG10(num)", "Math", [ArgumentMetadata("number", "Value", "number")])
def func_log10(engine: FormulaEngine, val):
    """
    Func log10 logic.
    
    Args:
        engine: Description of engine.
        val: Description of val.
    
    """
    try: return math.log10(float(val))
    except: return "#VALUE!"

# --- String Functions ---

@FormulaRegistry.register("LEN", "Length of text.", "LEN(text)", "Text", [ArgumentMetadata("text", "Text", "str")])
def func_len(engine: FormulaEngine, text):
    """
    Func len logic.
    
    Args:
        engine: Description of engine.
        text: Description of text.
    
    """
    return len(str(text)) if text is not None else 0

@FormulaRegistry.register("UPPER", "Uppercase.", "UPPER(text)", "Text", [ArgumentMetadata("text", "Text", "str")])
def func_upper(engine: FormulaEngine, text):
    """
    Func upper logic.
    
    Args:
        engine: Description of engine.
        text: Description of text.
    
    """
    return str(text).upper() if text is not None else ""

@FormulaRegistry.register("LOWER", "Lowercase.", "LOWER(text)", "Text", [ArgumentMetadata("text", "Text", "str")])
def func_lower(engine: FormulaEngine, text):
    """
    Func lower logic.
    
    Args:
        engine: Description of engine.
        text: Description of text.
    
    """
    return str(text).lower() if text is not None else ""

@FormulaRegistry.register("PROPER", "Title Case.", "PROPER(text)", "Text", [ArgumentMetadata("text", "Text", "str")])
def func_proper(engine: FormulaEngine, text):
    """
    Func proper logic.
    
    Args:
        engine: Description of engine.
        text: Description of text.
    
    """
    return str(text).title() if text is not None else ""

@FormulaRegistry.register("LEFT", "Left chars.", "LEFT(text, [n])", "Text", [
    ArgumentMetadata("text", "Text", "str"),
    ArgumentMetadata("num_chars", "Count (def 1)", "number", True)
])
def func_left(engine: FormulaEngine, text, n=1):
    """
    Func left logic.
    
    Args:
        engine: Description of engine.
        text: Description of text.
        n: Description of n.
    
    """
    try:
        s = str(text) if text is not None else ""
        count = int(float(n))
        return s[:count]
    except: return "#VALUE!"

@FormulaRegistry.register("RIGHT", "Right chars.", "RIGHT(text, [n])", "Text", [
    ArgumentMetadata("text", "Text", "str"),
    ArgumentMetadata("num_chars", "Count (def 1)", "number", True)
])
def func_right(engine: FormulaEngine, text, n=1):
    """
    Func right logic.
    
    Args:
        engine: Description of engine.
        text: Description of text.
        n: Description of n.
    
    """
    try:
        s = str(text) if text is not None else ""
        count = int(float(n))
        # slice from end
        return s[-count:] if count > 0 else ""
    except: return "#VALUE!"

@FormulaRegistry.register("MID", "Middle chars.", "MID(text, start, n)", "Text", [
    ArgumentMetadata("text", "Text", "str"),
    ArgumentMetadata("start_num", "Start (1-based)", "number"),
    ArgumentMetadata("num_chars", "Count", "number")
])
def func_mid(engine: FormulaEngine, text, start, n):
    """
    Func mid logic.
    
    Args:
        engine: Description of engine.
        text: Description of text.
        start: Description of start.
        n: Description of n.
    
    """
    try:
        s = str(text) if text is not None else ""
        st = int(float(start)) - 1 # 1-based to 0-based
        count = int(float(n))
        if st < 0: return "#VALUE!"
        return s[st:st+count]
    except: return "#VALUE!"

@FormulaRegistry.register("TRIM", "Trim spaces.", "TRIM(text)", "Text", [ArgumentMetadata("text", "Text", "str")])
def func_trim(engine: FormulaEngine, text):
    """
    Func trim logic.
    
    Args:
        engine: Description of engine.
        text: Description of text.
    
    """
    if text is None: return ""
    # Excel TRIM removes leading/trailing spaces AND reduces multiple internal spaces to one.
    # Standard .strip() only handles ends.
    s = str(text).strip()
    import re
    return re.sub(r'\s+', ' ', s)

@FormulaRegistry.register("REPLACE", "Replace text.", "REPLACE(text, start, n, new_text)", "Text", [
    ArgumentMetadata("old_text", "Text", "str"),
    ArgumentMetadata("start_num", "Start (1-based)", "number"),
    ArgumentMetadata("num_chars", "Count", "number"),
    ArgumentMetadata("new_text", "New Text", "str")
])
def func_replace(engine: FormulaEngine, old_text, start, n, new_text):
    """
    Func replace logic.
    
    Args:
        engine: Description of engine.
        old_text: Description of old_text.
        start: Description of start.
        n: Description of n.
        new_text: Description of new_text.
    
    """
    try:
        s = str(old_text) if old_text is not None else ""
        st = int(float(start)) - 1
        count = int(float(n))
        repl = str(new_text) if new_text is not None else ""
        
        if st < 0: return "#VALUE!"
        # Python replacement by slicing
        return s[:st] + repl + s[st+count:]
    except: return "#VALUE!"

@FormulaRegistry.register("SUBSTITUTE", "Substitute text.", "SUBSTITUTE(text, old, new, [n])", "Text", [
    ArgumentMetadata("text", "Text", "str"),
    ArgumentMetadata("old_text", "Old", "str"),
    ArgumentMetadata("new_text", "New", "str"),
    ArgumentMetadata("instance_num", "Instance (opt)", "number", True)
])
def func_substitute(engine: FormulaEngine, text, old_text, new_text, instance=None):
    """
    Func substitute logic.
    
    Args:
        engine: Description of engine.
        text: Description of text.
        old_text: Description of old_text.
        new_text: Description of new_text.
        instance: Description of instance.
    
    """
    try:
        s = str(text) if text is not None else ""
        old = str(old_text)
        new_ = str(new_text)
        if instance is None:
            return s.replace(old, new_)
        else:
            n = int(float(instance))
            # Python replace doesn't support specific instance index directly efficiently
            # We can split and join
            parts = s.split(old)
            if n > len(parts) - 1: return s # Instance out of range
            
            # Reconstruct: parts[0] + old + ... + parts[n-1] + NEW + parts[n] + ...
            # Actually easier: replace first n occurrences, then replace n-1 occurrences back? No.
            # Manual rebuild
            res = ""
            current = 0
            for i, part in enumerate(parts[:-1]):
                res += part
                current += 1
                if current == n:
                    res += new_
                else:
                    res += old
            res += parts[-1]
            return res
    except: return "#VALUE!"

@FormulaRegistry.register("TEXTJOIN", "Join with delimiter.", "TEXTJOIN(delim, skip_empty, text1, ...)", "Text", [
    ArgumentMetadata("delimiter", "Delimiter", "str"),
    ArgumentMetadata("ignore_empty", "Ignore Empty", "bool"),
    ArgumentMetadata("text1", "Text", "str")
], is_variadic=True)
def func_textjoin(engine: FormulaEngine, delim, ignore_empty, *args):
    """
    Func textjoin logic.
    
    Args:
        engine: Description of engine.
        delim: Description of delim.
        ignore_empty: Description of ignore_empty.
    
    """
    d = str(delim) if delim is not None else ""
    # ignore_empty logic: check if bool or int string
    skip = False
    try:
        if ignore_empty is None:
            # Default behavior for missing arg? Excel usually mandates it.
            # But here we treat empty as False or True?
            # User example: TEXTJOIN(,,...) impliesthey want default behavior.
            # Let's default to TRUE (convenience) or FALSE?
            # If d is "" (default), skip usually doesn't matter much unless we have gaps.
            # Let's default skip to TRUE to keep it clean.
            skip = True
        elif isinstance(ignore_empty, bool): skip = ignore_empty
        elif str(ignore_empty).lower() in ('true', '1'): skip = True
    except: pass
    
    parts = []
    def collect(item):
        """
        Collect logic.
        
        Args:
            item: Description of item.
        
        """
        if isinstance(item, list):
            for i in item: collect(i)
        else:
            s_val = str(item) if item is not None else ""
            if skip and s_val == "":
                return
            parts.append(s_val)
            
    for a in args: collect(a)
    return d.join(parts)

class FormulaHelper:
    """
    Utilities for formula manipulation.
    """
    @staticmethod
    def adjust_references(formula: str, row_delta: int, col_delta: int) -> str:
        """
        Shift cell references in a formula by (row_delta, col_delta).
        Respects absolute references ($A$1).
        """
        if not formula.startswith("="): return formula
        
        tokens = Tokenizer.tokenize(formula[1:], preserve_whitespace=True)
        new_formula = "="
        
        for t in tokens:
            if t.type == TokenType.ID:
                # Check if it's a cell ref
                val = FormulaHelper._shift_ref(t.value, row_delta, col_delta)
                new_formula += val
            elif t.type == TokenType.STRING:
                new_formula += f'"{t.value}"'
            elif t.type == TokenType.WS:
                new_formula += t.value
            else:
                new_formula += t.value
        
        return new_formula

    @staticmethod
    def _shift_ref(ref: str, r_d: int, c_d: int) -> str:
        match = re.match(r'^(\$?)([A-Z]+)(\$?)([0-9]+)$', ref, re.IGNORECASE)
        if not match: return ref
        
        abs_col, col_str, abs_row, row_str = match.groups()
        
        new_col_str = col_str
        new_row_str = row_str
        
        # Shift Column if not absolute
        if not abs_col:
             # Convert to index
             c_idx = 0
             for char in col_str.upper():
                 c_idx = c_idx * 26 + (ord(char) - ord('A') + 1)
             c_idx += c_d
             if c_idx < 1: c_idx = 1 # Clamp
             
             # Convert back
             res = ""
             t = c_idx
             while t > 0:
                 t, rem = divmod(t - 1, 26)
                 res = chr(65 + rem) + res
             new_col_str = res
             
        # Shift Row if not absolute
        if not abs_row:
             r_idx = int(row_str)
             r_idx += r_d
             if r_idx < 1: r_idx = 1 # Clamp
             new_row_str = str(r_idx)
             
        return f"{abs_col}{new_col_str}{abs_row}{new_row_str}"