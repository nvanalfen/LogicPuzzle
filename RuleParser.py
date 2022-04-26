from LogicPuzzle import LogicPuzzle
from Token import Token, TokenType

GRAMMAR_FILE = "Grammar.txt"

class InvalidTokenException(Exception):
    pass

class UnexpectedTokenException(Exception):
    pass

class MissingTokenException(Exception):
    pass

class GrammarNode:
    def __init__(self):
        self.next = {}
        self.value = -1

class RuleParser:
    def __init__(self):
        self.grammar = GrammarNode()
        self.read_grammar()

    def read_grammar(self):
        f = open(GRAMMAR_FILE)
        for line in f:
            if '%' in line:
                line = line[ :line.index('%') ]
            line = line.strip()
            if line.strip() == '':
                continue
            
            parts = line.split(":")
            tokens = parts[1].split(",")
            current_node = self.grammar
            for i in range(len(tokens)):
                el = tokens[i]
                tok_type = TokenType.get_type(el)
                if not tok_type == TokenType.INVALID and not tok_type in current_node.next:
                    # If the current noded doesn't have anything in the path you're following, add it
                    current_node.next[tok_type] = GrammarNode()
                # Advance a node
                current_node = current_node.next[tok_type]
                if i == len(tokens) - 1:
                    # Ending here makes this the rule given at the beginning of the line
                    current_node.value = float( parts[0] )
        f.close()

    # Simply read the lines form the rule file
    # Tokenize and parse later
    def read_rules(self, f_name):
        if f_name is None:
            return

        lines = []
        f = open(f_name)

        for line in f:
            if '#' in line:
                # Strip any comments out
                ind = line.index('#')
                line = line[:ind]
            lines.append( line.split() )

        f.close()
        return lines

    def tokenize(self, lines, puzzle:LogicPuzzle):
        tokenized_lines = []
        for line in lines:
            tokenized_lines.append( [ Token(el, puzzle) for el in line ] )
        
        return tokenized_lines

    def validate(self, lines):
        verified = []

        # Verify all the tokens are valid
        for i in range(len(lines)):
            line = lines[i]
            if any([ not(t.valid) for t in line ]):
                for j in range(len(line)):
                    if not line[j].valid:
                        raise InvalidTokenException( "Expression {}: Invalid token. Token {} - value = {}".format(i+1, j+1, str(line[j].value) ) )
        
        # Verify that the tokens satisfy the grammar
        for i in range(len(lines)):
            line = lines[i]
            current = self.grammar
            last = None
            for j in range(len(line)):
                if line[j].tok_type in current.next:
                    last = line[j]
                    current = current.next[ line[j].tok_type ]
                else:
                    raise UnexpectedTokenException( "Expression {}: Unexpected token. Token {} - value = {}, type = {}".format(i+1, j+1, str(line[j].value), str(line[j].tok_type) ) )
            
            if current.value == -1:
                raise MissingTokenException( "Expression {}: Expression ended early. Expected token after '{}', type = {}".format(i+1, str(last.value), str(last.tok_type) ) )
            verified.append( (current.value, line) )
        
        return verified

    def get_validated_rules(self, rule_f_name, puzzle:LogicPuzzle):
        lines = self.read_rules( rule_f_name )
        tokenized = self.tokenize( lines, puzzle )
        return self.validate( tokenized )