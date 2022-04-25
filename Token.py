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

class Token():
    
    def __init__(self, tok=None):
        self.tok_type = TokenType.INVALID
        self.value = tok
        self.valid = False

    # Set the type of token, the value, and whether or not it's a recognized token type
    def set_type(self, puzzle:LogicPuzzle):
        if self.is_inflexible_token():
            self.tok_type = self.get_inflexible_tok_type()
            self.valid = True
        elif Token.is_numerical(self.value):
            self.tok_type = TokenType.NUMBER
            self.valid = True
            self.value = float(self.value)
        elif "[" in self.value:
            self.validate_list_token(puzzle)
        elif "," in self.value:
            self.validate_pair_token(puzzle)
        else:
            self.validate_element_token(puzzle)
    
    # Check if a string can be cast to float
    def is_numerical(value):
        try:
            val = float(value)
            return True
        except:
            return False

    # Easier way to define tokens without flexible values
    # These are inflexible tokens (e.g. '=', '!=', '>', etc.)
    def is_inflexible_token(self):
        return (self.value == TokenType.EQUAL.value) or (self.value == TokenType.NOT_EQUAL.value) or \
            (self.value == TokenType.GT.value) or (self.value == TokenType.PLUS.value)

    # Return the value of a token without a flexible value
    # Return None if invalid token or token with flexible value (e.g. ELEMENT)
    def get_inflexible_tok_type(self):
        for tok_type in TokenType:
            if self.value == tok_type.value:
                return tok_type
        return None
    
    # Element is defined as a (category,value) tuple for a value in a category of the logic puzzle
    # Given a value (the token), check to make sure it's in the puzzled and return the category and value
    def get_element(self, puzzle:LogicPuzzle, value=None):
        if value is None:
            value = self.value

        # Because there is a numerical token type, categories with numerical values will be written as category_name:number
        if ":" in value:
            cat_A, el_A = value.split(":")
            if cat_A in puzzle.categories and Token.is_numerical(el_A) and float(el_A) in puzzle.category_values[cat_A]:
                return (cat_A, float(el_A))
            return None

        for category in puzzle.category_values:
            if value in puzzle.category_values[category]:
                return (category, value)
        return None

    # Given an token that doesn't fit in any otehr category, check to see if it's a valid element
    def validate_element_token(self, puzzle:LogicPuzzle):
        unit = self.get_element(puzzle)
        if unit is None:
            return
        
        self.tok_type = TokenType.ELEMENT
        self.valid = True
        self.value = unit

    # For tokens that have the '[' character, check to see if they're a list
    # Get rid of the edges, which should be brackets, split on commas, then check to make sure each 
    # element of the list is a valid Element token
    # Set the list of (category,value) pairs as the token 
    def validate_list_token(self, puzzle:LogicPuzzle):
        tok = self.value
        if tok[0] != "[" or tok[-1] != "]":
            return
        
        tok = tok[1:-1]
        elements = []
        for el in tok.split(","):
            unit = self.get_element(puzzle, el)
            if unit is None:
                return
            
            elements.append(unit)
        
        self.tok_type = TokenType.LIST
        self.valid = True
        self.value = elements

    # A pair token (not entirely accurately named after this function) is a comma separated pair of element,category
    # where element belongs to a different category that the one following the comma
    # For example, el_A,cat_B represents the set of elements in category B, related to element A (which is a member of category A)
    # This token is used when dealing with a category B that contains numerical values
    # Sets the token value to (cat_A, el_A, cat_B) to indicate which set of el_B items to map to
    def validate_pair_token(self, puzzle:LogicPuzzle):
        el_A, cat_B = self.value.split(",")
        unit = self.get_element(puzzle, el_A)

        if not unit is None:
            cat_A, el_A = unit
            if cat_B in puzzle.categories and cat_B != cat_A:
                self.tok_type = TokenType.PAIR
                self.valid = True
                self.value = (cat_A, el_A, cat_B)

