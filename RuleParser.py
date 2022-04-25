from LogicPuzzle import LogicPuzzle
from Token import Token

class RuleParser:
    def __init__(self, logic_puzzle, f_name):
        self.lp = logic_puzzle
        self.f_name = f_name

    # Simply read the lines form the rule file
    # Tokenize and parse later
    def read_rules(self):
        if self.f_name is None:
            return

        lines = []
        f = open(self.f_name)

        for line in f:
            if '#' in line:
                # Strip any comments out
                ind = line.index('#')
                line = line[:ind]
            lines.append( line.split() )

        return lines