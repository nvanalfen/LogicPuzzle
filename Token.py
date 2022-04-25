from LogicPuzzle import LogicPuzzle
from enum import Enum

class TokenType(Enum):
    EQUAL = "="
    NOT_EQUAL = "!="
    ELEMENT = "ELEMENT"
    LIST = "LIST"
    PAIR = "PAIR"
    GT = ">"
    PLUS = "+"
    NUMBER = "#"
    INVALID = "INV"

class Token(Enum):
    
    def __init__(self, tok):
        self.tok_type = TokenType.INVALID
        self.value = tok
        self.valid = False

    def set_type(self, tok, puzzle:LogicPuzzle):
        if self.is_inflexible_token(tok):
            self.tok_type = self.get_inflexible_tok_type(tok)
            self.valid = True
        elif Token.is_numerical(tok):
            self.tok_type = TokenType.NUMBER
            self.valid = True
            self.value = float(tok)
        elif "[" in tok:
            self.validate_list_token(tok, puzzle)
        elif "," in tok:
            self.validate_pair_token(tok)
        else:
            self.validate_element_token(tok)
    
    def is_numerical(value):
        try:
            val = float(value)
            return True
        except:
            return False

    # Easier way to define tokens without flexible values
    def is_inflexible_token(self, tok):
        return (tok == TokenType.EQUAL) or (tok == TokenType.NOT_EQUAL) or (tok == TokenType.GT) or (tok == TokenType.PLUS)

    # Return the value of a token without a flexible value
    # Return None if invalid token or token with flexible value (e.g. ELEMENT)
    def get_inflexible_tok_type(self, tok):
        for tok_type in TokenType:
            if tok == tok_type:
                return tok_type
        return None
    
    def get_element(self, tok, puzzle:LogicPuzzle):
        for category in puzzle.category_values:
            if tok in category:
                return (category, tok)
        return None

    def validate_element_token(self, tok, puzzle:LogicPuzzle):
        unit = self.get_element(tok, puzzle)
        if unit is None:
            return
        
        self.tok_type = TokenType.ELEMENT
        self.valid = True
        self.value = unit

    def validate_list_token(self, tok, puzzle:LogicPuzzle):
        if tok[0] != "[" or tok[-1] != "]":
            return
        
        tok = tok[1:-1]
        elements = []
        for el in tok.split(","):
            unit = self.get_element(el, puzzle)
            if unit is None:
                return
            
            elements.append(unit)
        
        self.tok_type = TokenType.ELEMENT
        self.valid = True
        self.value = elements

    def validate_pair_token(self, tok):
        pass
