import unittest
from LogicPuzzle import LogicPuzzle
from RuleParser import RuleParser, InvalidTokenException, UnexpectedTokenException, MissingTokenException
from Token import Token, TokenType
import os

# Test methods in LogicPuzzle
class LogicPuzzleTest(unittest.TestCase):

    ##### Test Setup Functions #####################################################################################################

    def test_read_categories(self):
        lp = LogicPuzzle()
        lp.read_categories( os.path.join("tests", "categories1.txt") )

        # Check that each category had been added properly
        assert( len(lp.categories) == 3 )
        assert( ("A" in lp.categories) and ("B" in lp.categories) and ("C" in lp.categories) )

        # Check that each category is the right length
        assert( len( lp.category_values["A"] )  == 3 )
        assert( len( lp.category_values["B"] ) == 3 )
        assert( len( lp.category_values["C"] ) == 3 )

        # Check that each category holds the right types of variables
        assert( all( [ isinstance(val, str) for val in lp.category_values["A"] ] ) )
        assert( all( [ isinstance(val, str) for val in lp.category_values["B"] ] ) )
        assert( all( [ isinstance(val, float) for val in lp.category_values["C"] ] ) )

        # Check that each category has the right values
        assert( all( [ val in lp.category_values["A"] for val in ["a1", "a2", "a3"] ] ) )
        assert( all( [ val in lp.category_values["B"] for val in ["b1", "b2", "b3"] ] ) )
        assert( all( [ val in lp.category_values["C"] for val in [1.0, 2.0, 3.0] ] ) )

    def test_read_rules(self):
        lp = LogicPuzzle()
        lp.read_categories( os.path.join("tests", "categories1.txt") )
        lp.create_sets()
        lp.rule_f_name = os.path.join("tests","rules1.txt")
        lp.read_rules()

        assert( lp.rules[0][0] == lp.a_is_b )
        assert( lp.rules[0][1] == ["A","a1","B","b1"] )

        assert( lp.rules[1][0] == lp.a_is_not_b )
        assert( lp.rules[1][1] == ["A","a2","B","b3"] )

        assert( lp.rules[2][0] == lp.exclusive_or )
        assert( lp.rules[2][1] == ["A","a2",[("B","b2"),("C",1.0)]] )

        assert( lp.rules[3][0] == lp.list_to_list )
        assert( lp.rules[3][1] == [[("A","a1"),("B","b2")],[("B","b1"),("C",2.0)]] )

        assert( lp.rules[4][0] == lp.a_greater_than_b )
        assert( lp.rules[4][1] == ["A","a1","B","b2","C"] )

        assert( lp.rules[5][0] == lp.a_greater_than_b )
        assert( lp.rules[5][1] == ["A","a2","B","b3","C",2] )

    def test_set_rules(self):
        lp = LogicPuzzle()
        lp.read_categories( os.path.join("tests", "categories1.txt") )
        lp.create_sets()
        rp = RuleParser()
        lines = rp.read_rules( os.path.join("tests","rules1.txt") )
        tokenized = rp.tokenize(lines, lp)
        validated = rp.validate(tokenized)
        lp.set_rules(validated)

        assert( lp.rules[0][0] == lp.a_is_b )
        assert( lp.rules[0][1] == ["A","a1","B","b1"] )

        assert( lp.rules[1][0] == lp.a_is_not_b )
        assert( lp.rules[1][1] == ["A","a2","B","b3"] )

        assert( lp.rules[2][0] == lp.exclusive_or )
        assert( lp.rules[2][1] == ["A","a2",[("B","b2"),("C",1.0)]] )

        assert( lp.rules[3][0] == lp.list_to_list )
        assert( lp.rules[3][1] == [[("A","a1"),("B","b2")],[("B","b1"),("C",2.0)]] )

        assert( lp.rules[4][0] == lp.a_greater_than_b )
        assert( lp.rules[4][1] == ["A","a1","B","b2","C"] )

        assert( lp.rules[5][0] == lp.a_greater_than_b )
        assert( lp.rules[5][1] == ["A","a2","B","b3","C",2] )

    def test_extract_params(self):
        lp = LogicPuzzle()
        lp.read_categories( os.path.join("tests", "categories1.txt") )
        lp.create_sets()
        rp = RuleParser()
        lines = rp.read_rules( os.path.join("tests","rules1.txt") )
        tokenized = rp.tokenize(lines, lp)
        validated = rp.validate(tokenized)

        params = lp.extract_params( validated[0][1] )
        assert( params == ["A","a1","B","b1"] )

        params = lp.extract_params( validated[1][1] )
        assert( params == ["A","a2","B","b3"] )

        params = lp.extract_params( validated[2][1] )
        assert( params == ["A","a2",[("B","b2"),("C",1.0)]] )

        params = lp.extract_params( validated[3][1] )
        assert( params == [[("A","a1"),("B","b2")],[("B","b1"),("C",2.0)]] )

        params = lp.extract_params( validated[4][1] )
        assert( params == ["A","a1","B","b2","C"] )

        params = lp.extract_params( validated[5][1] )
        assert( params == ["A","a2","B","b3","C",2] )

    def test_create_sets(self):
        lp = LogicPuzzle()
        lp.read_categories( os.path.join("tests", "categories1.txt") )

        lp.create_sets()

        a_keys = [ ("B", "b1", "A"), ("B", "b2", "A"), ("B", "b3", "A"), ("C", 1.0, "A"), ("C", 2.0, "A"), ("C", 3.0, "A") ]
        b_keys = [ ("A","a1","B"), ("A","a2","B"), ("A","a3","B"), ("C", 1.0, "B"), ("C", 2.0, "B"), ("C", 3.0, "B") ]
        c_keys = [ ("A","a1","C"), ("A","a2","C"), ("A","a3","C"), ("B", "b1", "C"), ("B", "b2", "C"), ("B", "b3", "C") ]

        assert( len( lp.full_sets ) == 18 )

        # Make sure all the right keys exist
        assert( all( [ key in lp.full_sets for key in a_keys+b_keys+c_keys ] ) )

        # Make sure each key maps to the right set
        assert( all( [ lp.full_sets[key] == lp.category_values["A"] for key in a_keys ] ) )
        assert( all( [ lp.full_sets[key] == lp.category_values["B"] for key in b_keys ] ) )
        assert( all( [ lp.full_sets[key] == lp.category_values["C"] for key in c_keys ] ) )
    
    ##### Test Auxilliary Funcitons ################################################################################################

    def test_subset(self):
        lp = LogicPuzzle()

        a = set([1,2,3,4,5])
        b = set([3,4,5,6,7])

        # Check general greater than
        a_sub, b_sub = lp.subset(a,b)
        assert( a_sub == set([4,5]) )
        assert( b_sub == set([3,4]) )

        b_sub, a_sub = lp.subset(b,a)
        assert( b_sub == b )
        assert( a_sub == a )

        # Check with a specific number given
        a_sub, b_sub = lp.subset(a,b,val=2)
        assert( a_sub == set([5]) )
        assert( b_sub == set([3]) )

        b_sub, a_sub = lp.subset(b,a,val=2)
        assert( b_sub == b )
        assert( a_sub == a )
    
    def test_is_complete(self):
        lp = LogicPuzzle()

        assert( not lp.is_complete() )
        lp.read_categories( os.path.join("tests", "categories1.txt") )
        lp.create_sets()
        assert( not lp.is_complete() )
        for key in lp.full_sets:
            lp.full_sets[key] = set([ lp.full_sets[key].pop() ])
        assert( lp.is_complete() )

    ##### Test Rule Functions ######################################################################################################

    def test_a_is_not_b(self):
        lp = LogicPuzzle()
        lp.read_categories( os.path.join("tests", "categories1.txt") )
        lp.create_sets()

        set_key_A = ("A", "a1", "B")
        set_key_B = ("B", "b1", "A")
        
        lp.a_is_not_b("A", "a1", "B", "b1")

        for key in lp.full_sets:
            if key == set_key_A:
                assert( lp.full_sets[key] == set(["b2", "b3"]) )
            elif key == set_key_B:
                assert( lp.full_sets[key] == set(["a2", "a3"]) )
            else:
                assert( len( lp.full_sets[key] ) == 3 )
    
    def test_a_is_b(self):
        lp = LogicPuzzle()
        lp.read_categories( os.path.join("tests", "categories1.txt") )
        lp.create_sets()

        set_key_A = ("A", "a1", "B")
        set_key_B = ("B", "b1", "A")
        changed_keys = [ ("A", "a2", "B"), ("A", "a3", "B"), ("B","b2","A"), ("B", "b3", "A") ]
        
        lp.a_is_b("A", "a1", "B", "b1")

        for key in lp.full_sets:
            if key == set_key_A:
                assert( lp.full_sets[key] == set(["b1"]) )
            elif key == set_key_B:
                assert( lp.full_sets[key] == set(["a1"]) )
            elif key in changed_keys:
                assert( len( lp.full_sets[key] ) == 2 )
            else:
                assert( len( lp.full_sets[key] ) == 3 )
    
    def test_exclusive_or(self):
        lp = LogicPuzzle()
        lp.read_categories( os.path.join("tests", "categories1.txt") )
        lp.create_sets()

        set_key_B = ("B", "b1", "C")
        set_key_C = ("C", 1.0, "B")

        lp.exclusive_or("A","a1","B","b1","C",1.0)

        assert( lp.full_sets[ set_key_B ] == set( [2.0, 3.0] ) )
        assert( lp.full_sets[ set_key_C ] == set( ["b2", "b3"] ) )
        for key in lp.full_sets:
            if key != set_key_B and key != set_key_C:
                assert( len( lp.full_sets[key] ) == 3 )
        
        lp.full_sets[ ("A", "a1", "B") ].remove("b1")
        lp.exclusive_or("A","a1","B","b1","C",1.0)

        assert( lp.full_sets[("A","a1","B")] == set(["b2", "b3"]) )
        assert( lp.full_sets[("A","a2","B")] == set(["b1", "b2", "b3"]) )
        assert( lp.full_sets[("A","a3","B")] == set(["b1", "b2", "b3"]) )
        assert( lp.full_sets[("A","a1","C")] == set([1.0]) )
        assert( lp.full_sets[("A","a2","C")] == set([2.0, 3.0]) )
        assert( lp.full_sets[("A","a3","C")] == set([2.0, 3.0]) )
        assert( lp.full_sets[set_key_B] == set( [2.0, 3.0] ) )
        assert( lp.full_sets[("B","b2","C")] == set([1.0, 2.0, 3.0]) )
        assert( lp.full_sets[("B","b3","C")] == set([1.0, 2.0, 3.0]) )

        assert( lp.full_sets[("B","b1","A")] == set(["a2", "a3"]) )
        assert( lp.full_sets[("B","b2","A")] == set(["a1", "a2", "a3"]) )
        assert( lp.full_sets[("B","b3","A")] == set(["a1", "a2", "a3"]) )
        assert( lp.full_sets[("C",1.0,"A")] == set(["a1"]) )
        assert( lp.full_sets[("C",2.0,"A")] == set(["a2", "a3"]) )
        assert( lp.full_sets[("C",3.0,"A")] == set(["a2", "a3"]) )
        assert( lp.full_sets[set_key_C] == set( ["b2", "b3"] ) )
        assert( lp.full_sets[("C",2.0,"B")] == set(["b1", "b2", "b3"]) )
        assert( lp.full_sets[("C",3.0,"B")] == set(["b1", "b2", "b3"]) )

    def test_list_to_list(self):
        lp = LogicPuzzle()
        lp.read_categories( os.path.join("tests", "categories1.txt") )
        lp.create_sets()

        N_star = [("A","a1"), ("B","b1")]
        M_star = [("C","c1"), ("C","c2")]

        lp.list_to_list(N_star, M_star)

        assert( lp.full_sets[("A","a1","B")] == set(["b2", "b3"]) )
        assert( lp.full_sets[("A","a2","B")] == set(["b1", "b2", "b3"]) )
        assert( lp.full_sets[("A","a3","B")] == set(["b1", "b2", "b3"]) )
        assert( lp.full_sets[("A","a1","C")] == set([1.0, 2.0, 3.0]) )
        assert( lp.full_sets[("A","a2","C")] == set([1.0, 2.0, 3.0]) )
        assert( lp.full_sets[("A","a3","C")] == set([1.0, 2.0, 3.0]) )
        assert( lp.full_sets[("B","b1","C")] == set([1.0, 2.0, 3.0]) )
        assert( lp.full_sets[("B","b2","C")] == set([1.0, 2.0, 3.0]) )
        assert( lp.full_sets[("B","b3","C")] == set([1.0, 2.0, 3.0]) )

        assert( lp.full_sets[("B","b1","A")] == set(["a2", "a3"]) )
        assert( lp.full_sets[("B","b2","A")] == set(["a1", "a2", "a3"]) )
        assert( lp.full_sets[("B","b3","A")] == set(["a1", "a2", "a3"]) )
        assert( lp.full_sets[("C",1.0,"A")] == set(["a1", "a2", "a3"]) )
        assert( lp.full_sets[("C",2.0,"A")] == set(["a1", "a2", "a3"]) )
        assert( lp.full_sets[("C",3.0,"A")] == set(["a1", "a2", "a3"]) )
        assert( lp.full_sets[("C",1.0,"B")] == set(["b1", "b2", "b3"]) )
        assert( lp.full_sets[("C",2.0,"B")] == set(["b1", "b2", "b3"]) )
        assert( lp.full_sets[("C",3.0,"B")] == set(["b1", "b2", "b3"]) )

    def test_a_greater_than_b(self):
        lp = LogicPuzzle()
        lp.read_categories( os.path.join("tests", "categories1.txt") )
        lp.create_sets()

        lp.a_greater_than_b("A", "a1", "B", "b1", "C")

        # Test the general greater than
        # This function leaves some values that should be eliminated
        # This is ok. Getting rid of them is beyond the scope of this function and will be handled by other logic functions
        assert( lp.full_sets[("A","a1","B")] == set(["b2", "b3"]) )
        assert( lp.full_sets[("A","a2","B")] == set(["b1", "b2", "b3"]) )
        assert( lp.full_sets[("A","a3","B")] == set(["b1", "b2", "b3"]) )
        assert( lp.full_sets[("A","a1","C")] == set([2.0, 3.0]) )
        assert( lp.full_sets[("A","a2","C")] == set([1.0, 2.0, 3.0]) )
        assert( lp.full_sets[("A","a3","C")] == set([1.0, 2.0, 3.0]) )
        assert( lp.full_sets[("B","b1","C")] == set([1.0, 2.0]) )
        assert( lp.full_sets[("B","b2","C")] == set([1.0, 2.0, 3.0]) )
        assert( lp.full_sets[("B","b3","C")] == set([1.0, 2.0, 3.0]) )

        assert( lp.full_sets[("B","b1","A")] == set(["a2", "a3"]) )
        assert( lp.full_sets[("B","b2","A")] == set(["a1", "a2", "a3"]) )
        assert( lp.full_sets[("B","b3","A")] == set(["a1", "a2", "a3"]) )
        assert( lp.full_sets[("C",1.0,"A")] == set(["a1", "a2", "a3"]) )        # This line will lose a1 from logic later
        assert( lp.full_sets[("C",2.0,"A")] == set(["a1", "a2", "a3"]) )
        assert( lp.full_sets[("C",3.0,"A")] == set(["a1", "a2", "a3"]) )
        assert( lp.full_sets[("C",1.0,"B")] == set(["b1", "b2", "b3"]) )
        assert( lp.full_sets[("C",2.0,"B")] == set(["b1", "b2", "b3"]) )
        assert( lp.full_sets[("C",3.0,"B")] == set(["b1", "b2", "b3"]) )        # This line will lose b1 from logic later

        lp.create_sets()
        lp.a_greater_than_b("A", "a1", "B", "b1", "C", val=2)
        # Test greater by an amount
        # similar to above, other logic functions will further eliminate candidates
        assert( lp.full_sets[("A","a1","B")] == set(["b2", "b3"]) )
        assert( lp.full_sets[("A","a2","B")] == set(["b1", "b2", "b3"]) )
        assert( lp.full_sets[("A","a3","B")] == set(["b1", "b2", "b3"]) )
        assert( lp.full_sets[("A","a1","C")] == set([3.0]) )
        assert( lp.full_sets[("A","a2","C")] == set([1.0, 2.0, 3.0]) )
        assert( lp.full_sets[("A","a3","C")] == set([1.0, 2.0, 3.0]) )
        assert( lp.full_sets[("B","b1","C")] == set([1.0]) )
        assert( lp.full_sets[("B","b2","C")] == set([1.0, 2.0, 3.0]) )
        assert( lp.full_sets[("B","b3","C")] == set([1.0, 2.0, 3.0]) )

        assert( lp.full_sets[("B","b1","A")] == set(["a2", "a3"]) )
        assert( lp.full_sets[("B","b2","A")] == set(["a1", "a2", "a3"]) )
        assert( lp.full_sets[("B","b3","A")] == set(["a1", "a2", "a3"]) )
        assert( lp.full_sets[("C",1.0,"A")] == set(["a1", "a2", "a3"]) )
        assert( lp.full_sets[("C",2.0,"A")] == set(["a1", "a2", "a3"]) )
        assert( lp.full_sets[("C",3.0,"A")] == set(["a1", "a2", "a3"]) )
        assert( lp.full_sets[("C",1.0,"B")] == set(["b1", "b2", "b3"]) )
        assert( lp.full_sets[("C",2.0,"B")] == set(["b1", "b2", "b3"]) )
        assert( lp.full_sets[("C",3.0,"B")] == set(["b1", "b2", "b3"]) )

    ##### Test General Logic Funcitons #############################################################################################

    def test_reflexive_inclusion_one_element(self):
        lp = LogicPuzzle()
        lp.read_categories( os.path.join("tests", "categories1.txt") )
        lp.create_sets()

        lp.full_sets[("A","a1","B")] = set(["b1"])
        lp.reflexive_inclusion()

        assert( lp.full_sets[("A","a1","B")] == set(["b1"]) )
        assert( lp.full_sets[("A","a2","B")] == set(["b2", "b3"]) )
        assert( lp.full_sets[("A","a3","B")] == set(["b2", "b3"]) )
        assert( lp.full_sets[("A","a1","C")] == set([1.0, 2.0, 3.0]) )
        assert( lp.full_sets[("A","a2","C")] == set([1.0, 2.0, 3.0]) )
        assert( lp.full_sets[("A","a3","C")] == set([1.0, 2.0, 3.0]) )
        assert( lp.full_sets[("B","b1","C")] == set([1.0, 2.0, 3.0]) )
        assert( lp.full_sets[("B","b2","C")] == set([1.0, 2.0, 3.0]) )
        assert( lp.full_sets[("B","b3","C")] == set([1.0, 2.0, 3.0]) )

        assert( lp.full_sets[("B","b1","A")] == set(["a1"]) )
        assert( lp.full_sets[("B","b2","A")] == set(["a2", "a3"]) )
        assert( lp.full_sets[("B","b3","A")] == set(["a2", "a3"]) )
        assert( lp.full_sets[("C",1.0,"A")] == set(["a1", "a2", "a3"]) )
        assert( lp.full_sets[("C",2.0,"A")] == set(["a1", "a2", "a3"]) )
        assert( lp.full_sets[("C",3.0,"A")] == set(["a1", "a2", "a3"]) )
        assert( lp.full_sets[("C",1.0,"B")] == set(["b1", "b2", "b3"]) )
        assert( lp.full_sets[("C",2.0,"B")] == set(["b1", "b2", "b3"]) )
        assert( lp.full_sets[("C",3.0,"B")] == set(["b1", "b2", "b3"]) )

    def test_reflexive_inclusion_two_element(self):
        lp = LogicPuzzle()
        lp.read_categories( os.path.join("tests", "categories1.txt") )
        lp.create_sets()

        lp.full_sets[("A","a1","B")] = set(["b1"])
        lp.full_sets[("B","b2","A")] = set(["a2"])
        lp.reflexive_inclusion()

        assert( lp.full_sets[("A","a1","B")] == set(["b1"]) )
        assert( lp.full_sets[("A","a2","B")] == set(["b2"]) )
        assert( lp.full_sets[("A","a3","B")] == set(["b3"]) )
        assert( lp.full_sets[("A","a1","C")] == set([1.0, 2.0, 3.0]) )
        assert( lp.full_sets[("A","a2","C")] == set([1.0, 2.0, 3.0]) )
        assert( lp.full_sets[("A","a3","C")] == set([1.0, 2.0, 3.0]) )
        assert( lp.full_sets[("B","b1","C")] == set([1.0, 2.0, 3.0]) )
        assert( lp.full_sets[("B","b2","C")] == set([1.0, 2.0, 3.0]) )
        assert( lp.full_sets[("B","b3","C")] == set([1.0, 2.0, 3.0]) )

        assert( lp.full_sets[("B","b1","A")] == set(["a1"]) )
        assert( lp.full_sets[("B","b2","A")] == set(["a2"]) )
        assert( lp.full_sets[("B","b3","A")] == set(["a3"]) )
        assert( lp.full_sets[("C",1.0,"A")] == set(["a1", "a2", "a3"]) )
        assert( lp.full_sets[("C",2.0,"A")] == set(["a1", "a2", "a3"]) )
        assert( lp.full_sets[("C",3.0,"A")] == set(["a1", "a2", "a3"]) )
        assert( lp.full_sets[("C",1.0,"B")] == set(["b1", "b2", "b3"]) )
        assert( lp.full_sets[("C",2.0,"B")] == set(["b1", "b2", "b3"]) )
        assert( lp.full_sets[("C",3.0,"B")] == set(["b1", "b2", "b3"]) )

    def test_reflexive_exclusion(self):
        lp = LogicPuzzle()
        lp.read_categories( os.path.join("tests", "categories1.txt") )
        lp.create_sets()

        lp.a_is_b("A","a1","B","b1")
        lp.full_sets[("B","b1","C")] = set([1.0])

        lp.reflexive_exclusion()

        assert( lp.full_sets[("A","a1","B")] == set(["b1"]) )
        assert( lp.full_sets[("A","a2","B")] == set(["b2", "b3"]) )
        assert( lp.full_sets[("A","a3","B")] == set(["b2", "b3"]) )
        assert( lp.full_sets[("A","a1","C")] == set([1.0, 2.0, 3.0]) )
        assert( lp.full_sets[("A","a2","C")] == set([1.0, 2.0, 3.0]) )
        assert( lp.full_sets[("A","a3","C")] == set([1.0, 2.0, 3.0]) )
        assert( lp.full_sets[("B","b1","C")] == set([1.0]) )
        assert( lp.full_sets[("B","b2","C")] == set([1.0, 2.0, 3.0]) )
        assert( lp.full_sets[("B","b3","C")] == set([1.0, 2.0, 3.0]) )

        assert( lp.full_sets[("B","b1","A")] == set(["a1"]) )
        assert( lp.full_sets[("B","b2","A")] == set(["a2", "a3"]) )
        assert( lp.full_sets[("B","b3","A")] == set(["a2", "a3"]) )
        assert( lp.full_sets[("C",1.0,"A")] == set(["a1", "a2", "a3"]) )
        assert( lp.full_sets[("C",2.0,"A")] == set(["a1", "a2", "a3"]) )
        assert( lp.full_sets[("C",3.0,"A")] == set(["a1", "a2", "a3"]) )
        assert( lp.full_sets[("C",1.0,"B")] == set(["b1", "b2", "b3"]) )
        assert( lp.full_sets[("C",2.0,"B")] == set(["b2", "b3"]) )
        assert( lp.full_sets[("C",3.0,"B")] == set(["b2", "b3"]) )

    def test_link_inclusion(self):
        lp = LogicPuzzle()
        lp.read_categories( os.path.join("tests", "categories1.txt") )
        lp.create_sets()

        lp.full_sets[("A","a1","B")].remove("b1")
        lp.full_sets[("B","b2","C")].remove(1.0)
        lp.full_sets[("B","b2","C")].remove(2.0)
        lp.full_sets[("B","b3","C")].remove(1.0)
        lp.full_sets[("B","b3","C")].remove(3.0)

        lp.link_inclusion()

        assert( lp.full_sets[("A","a1","B")] == set(["b2", "b3"]) )
        assert( lp.full_sets[("A","a2","B")] == set(["b1", "b2", "b3"]) )
        assert( lp.full_sets[("A","a3","B")] == set(["b1", "b2", "b3"]) )
        assert( lp.full_sets[("A","a1","C")] == set([2.0, 3.0]) )
        assert( lp.full_sets[("A","a2","C")] == set([1.0, 2.0, 3.0]) )
        assert( lp.full_sets[("A","a3","C")] == set([1.0, 2.0, 3.0]) )
        assert( lp.full_sets[("B","b1","C")] == set([1.0, 2.0, 3.0]) )
        assert( lp.full_sets[("B","b2","C")] == set([3.0]) )
        assert( lp.full_sets[("B","b3","C")] == set([2.0]) )

        assert( lp.full_sets[("B","b1","A")] == set(["a1", "a2", "a3"]) )
        assert( lp.full_sets[("B","b2","A")] == set(["a1", "a2", "a3"]) )
        assert( lp.full_sets[("B","b3","A")] == set(["a1", "a2", "a3"]) )
        assert( lp.full_sets[("C",1.0,"A")] == set(["a1", "a2", "a3"]) )
        assert( lp.full_sets[("C",2.0,"A")] == set(["a1", "a2", "a3"]) )
        assert( lp.full_sets[("C",3.0,"A")] == set(["a1", "a2", "a3"]) )
        assert( lp.full_sets[("C",1.0,"B")] == set(["b1", "b2", "b3"]) )
        assert( lp.full_sets[("C",2.0,"B")] == set(["b1", "b2", "b3"]) )
        assert( lp.full_sets[("C",3.0,"B")] == set(["b1", "b2", "b3"]) )

    def test_link_exclusion(self):
        lp = LogicPuzzle()
        lp.read_categories( os.path.join("tests", "categories1.txt") )
        lp.create_sets()

        lp.full_sets[("A","a1","B")].remove("b1")
        lp.a_is_b("B","b1","C",1.0)

        lp.link_exclusion()

        assert( lp.full_sets[("A","a1","B")] == set(["b2", "b3"]) )
        assert( lp.full_sets[("A","a2","B")] == set(["b1", "b2", "b3"]) )
        assert( lp.full_sets[("A","a3","B")] == set(["b1", "b2", "b3"]) )
        assert( lp.full_sets[("A","a1","C")] == set([2.0, 3.0]) )
        assert( lp.full_sets[("A","a2","C")] == set([1.0, 2.0, 3.0]) )
        assert( lp.full_sets[("A","a3","C")] == set([1.0, 2.0, 3.0]) )
        assert( lp.full_sets[("B","b1","C")] == set([1.0]) )
        assert( lp.full_sets[("B","b2","C")] == set([2.0, 3.0]) )
        assert( lp.full_sets[("B","b3","C")] == set([2.0, 3.0]) )

        assert( lp.full_sets[("B","b1","A")] == set(["a1", "a2", "a3"]) )
        assert( lp.full_sets[("B","b2","A")] == set(["a1", "a2", "a3"]) )
        assert( lp.full_sets[("B","b3","A")] == set(["a1", "a2", "a3"]) )
        assert( lp.full_sets[("C",1.0,"A")] == set(["a1", "a2", "a3"]) )
        assert( lp.full_sets[("C",2.0,"A")] == set(["a1", "a2", "a3"]) )
        assert( lp.full_sets[("C",3.0,"A")] == set(["a1", "a2", "a3"]) )
        assert( lp.full_sets[("C",1.0,"B")] == set(["b1"]) )
        assert( lp.full_sets[("C",2.0,"B")] == set(["b2", "b3"]) )
        assert( lp.full_sets[("C",3.0,"B")] == set(["b2", "b3"]) )

# Test methods in Token
class TokenTest(unittest.TestCase):

    def test_is_inflexible_token(self):
        lp = LogicPuzzle()
        lp.read_categories( os.path.join("tests", "categories1.txt") )
        lp.create_sets()

        tok = Token("=")
        assert( tok.is_inflexible_token() )

        tok = Token("!=")
        assert( tok.is_inflexible_token() )

        tok = Token(">")
        assert( tok.is_inflexible_token() )

        tok = Token("+")
        assert( tok.is_inflexible_token() )

    def test_get_element(self):
        lp = LogicPuzzle()
        lp.read_categories( os.path.join("tests", "categories1.txt") )
        lp.create_sets()

        tok = Token("a1")
        result = tok.get_element(lp)
        assert( result == ("A","a1") )

        tok = Token("c1")
        result = tok.get_element(lp)
        assert( result is None )

    def test_validate_element_token(self):
        lp = LogicPuzzle()
        lp.read_categories( os.path.join("tests", "categories1.txt") )
        lp.create_sets()

        tok = Token("a1")
        tok.validate_element_token(lp)
        assert( tok.valid )
        assert( tok.tok_type == TokenType.ELEMENT )
        assert( tok.value == ("A","a1") )

        tok = Token("c1")
        tok.validate_element_token(lp)
        assert( not tok.valid )
        assert( tok.tok_type == TokenType.INVALID )
        assert( tok.value == "c1" )

    def test_validate_list_token(self):
        lp = LogicPuzzle()
        lp.read_categories( os.path.join("tests", "categories1.txt") )
        lp.create_sets()

        tok = Token("[a1,b1]")
        tok.validate_list_token(lp)
        assert( tok.valid )
        assert( tok.tok_type == TokenType.LIST )
        assert( tok.value == [("A","a1"), ("B","b1")] )

        tok = Token("[a1,b1,c1]")
        tok.validate_list_token(lp)
        assert( not tok.valid )
        assert( tok.tok_type == TokenType.INVALID )
        assert( tok.value == "[a1,b1,c1]" )

    def test_validate_pair_token(self):
        lp = LogicPuzzle()
        lp.read_categories( os.path.join("tests", "categories1.txt") )
        lp.create_sets()

        tok = Token("a1,C")
        tok.validate_pair_token(lp)
        assert( tok.valid )
        assert( tok.tok_type == TokenType.PAIR )
        assert( tok.value == ("A", "a1", "C") )

        tok = Token(",C")
        tok.validate_pair_token(lp)
        assert( not tok.valid )
        assert( tok.tok_type == TokenType.INVALID )
        assert( tok.value == ",C" )

        tok = Token("b4,C")
        tok.validate_pair_token(lp)
        assert( not tok.valid )
        assert( tok.tok_type == TokenType.INVALID )
        assert( tok.value == "b4,C" )

        tok = Token(",")
        tok.validate_pair_token(lp)
        assert( not tok.valid )
        assert( tok.tok_type == TokenType.INVALID )
        assert( tok.value == "," )

    def test_set_type(self):
        lp = LogicPuzzle()
        lp.read_categories( os.path.join("tests", "categories1.txt") )
        lp.create_sets()

        tok = Token("=")
        tok.set_type(lp)
        assert( tok.valid )
        assert( tok.tok_type == TokenType.EQUAL )
        assert( tok.value == "=" )

        tok = Token("!=")
        tok.set_type(lp)
        assert( tok.valid )
        assert( tok.tok_type == TokenType.NOT_EQUAL )
        assert( tok.value == "!=" )

        tok = Token(">")
        tok.set_type(lp)
        assert( tok.valid )
        assert( tok.tok_type == TokenType.GT )
        assert( tok.value == ">" )

        tok = Token("+")
        tok.set_type(lp)
        assert( tok.valid )
        assert( tok.tok_type == TokenType.PLUS )
        assert( tok.value == "+" )

        tok = Token("5")
        tok.set_type(lp)
        assert( tok.valid )
        assert( tok.tok_type == TokenType.NUMBER )
        assert( tok.value == 5.0 )

        tok = Token("b2")
        tok.set_type(lp)
        assert( tok.valid )
        assert( tok.tok_type == TokenType.ELEMENT )
        assert( tok.value == ("B","b2") )

        tok = Token("C:2")
        tok.set_type(lp)
        assert( tok.valid )
        assert( tok.tok_type == TokenType.ELEMENT )
        assert( tok.value == ("C",2.0) )

        tok = Token("b2,C")
        tok.set_type(lp)
        assert( tok.valid )
        assert( tok.tok_type == TokenType.PAIR )
        assert( tok.value == ("B","b2","C") )

        tok = Token("[a1,a2,b1,C:2]")
        tok.set_type(lp)
        assert( tok.valid )
        assert( tok.tok_type == TokenType.LIST )
        assert( tok.value == [("A","a1"),("A","a2"),("B","b1"),("C",2.0)] )

        tok = Token("a4")
        tok.set_type(lp)
        assert( not tok.valid )
        assert( tok.tok_type == TokenType.INVALID )
        assert( tok.value == "a4" )

# Test methods in RuleParser
class RuleParserTest(unittest.TestCase):
    
    def test_read_rules(self):
        lp = LogicPuzzle()
        rp = RuleParser()
        lines = rp.read_rules(os.path.join("tests","rules1.txt"))

        assert( len(lines) == 6 )
        assert( lines[0] == ["a1", "=", "b1"] )
        assert( lines[1] == ["a2", "!=", "b3"] )
        assert( lines[2] == ["a2", "=", "[b2,C:1]"] )
        assert( lines[3] == ["[a1,b2]", "=", "[b1,C:2]"] )
        assert( lines[4] == ["a1,C", ">", "b2,C"] )
        assert( lines[5] == ["a2,C", "=", "b3,C", "+", "2"] )

    def test_read_grammar(self):
        lp = LogicPuzzle()
        lp.read_categories( os.path.join("tests", "categories1.txt") )
        lp.create_sets()
        rp = RuleParser()
        rp.read_grammar()

        # 6 Paths so far
        # ELEMENT,=,ELEMENT
        # ELEMENT,!=,ELEMENT
        # ELEMENT,=,LIST
        # LIST,=,LIST
        # PAIR,>,PAIR
        # PAIR,=,PAIR,+,#

        node = rp.grammar
        # Make sure the right keys are at the first level and none of them have a value
        assert( len( node.next ) == 3 )
        assert( all( [ t in node.next for t in [TokenType.ELEMENT, TokenType.PAIR, TokenType.LIST] ] ) )
        assert( all( [ node.next[t].value == -1 for t in node.next ] ) )

        # Follow the ELEMENT path first
        node = node.next[TokenType.ELEMENT]
        assert( len( node.next ) == 2 )
        assert( all( [ t in node.next for t in [TokenType.EQUAL, TokenType.NOT_EQUAL] ] ) )
        assert( all( [ node.next[t].value == -1 for t in node.next ] ) )
        # Continue forward one more to the = path
        node = node.next[TokenType.EQUAL]
        assert( len( node.next ) == 2 )
        assert( all( [ t in node.next for t in [TokenType.ELEMENT, TokenType.LIST] ] ) )
        assert( node.next[TokenType.ELEMENT].value == 1 )
        assert( node.next[TokenType.LIST].value == 3 )
        assert( len(node.next[TokenType.ELEMENT].next) == 0 )
        assert( len(node.next[TokenType.LIST].next) == 0 )

        # Back up to the ELEMENT,!= path
        node = rp.grammar
        node = node.next[TokenType.ELEMENT]
        node = node.next[TokenType.NOT_EQUAL]
        assert( len( node.next ) == 1 )
        assert( node.next[TokenType.ELEMENT].value == 2 )
        assert( len(node.next[TokenType.ELEMENT].next) == 0 )

        # Back up and check the LIST path
        node = rp.grammar
        node = node.next[TokenType.LIST]
        assert( len( node.next ) == 1 )
        assert( node.next[TokenType.EQUAL].value == -1 )
        node = node.next[TokenType.EQUAL]
        assert( len( node.next ) == 1 )
        assert( node.next[TokenType.LIST].value == 4 )
        assert( len(node.next[TokenType.LIST].next) == 0 )

        # Back up and check the PAIR path
        node = rp.grammar
        node = node.next[TokenType.PAIR]
        assert( len( node.next ) == 2 )
        assert( node.next[TokenType.GT].value == -1 )
        assert( node.next[TokenType.EQUAL].value == -1 )
        # Check the > Path
        node = node.next[TokenType.GT]
        assert( len( node.next ) == 1 )
        assert( node.next[TokenType.PAIR].value == 5 )
        assert( len(node.next[TokenType.PAIR].next) == 0 )
        # Back up again to the PAIR,= path
        node = rp.grammar
        node = node.next[TokenType.PAIR]
        node = node.next[TokenType.EQUAL]
        assert( len( node.next ) == 1 )
        assert( node.next[TokenType.PAIR].value == -1 )
        node = node.next[TokenType.PAIR]
        assert( len( node.next ) == 1 )
        assert( node.next[TokenType.PLUS].value == -1 )
        node = node.next[TokenType.PLUS]
        assert( len( node.next ) == 1 )
        assert( node.next[TokenType.NUMBER].value == 5 )
        assert( len(node.next[TokenType.NUMBER].next) == 0 )

    def test_tokenize(self):
        lp = LogicPuzzle()
        lp.read_categories( os.path.join("tests", "categories1.txt") )
        lp.create_sets()
        rp = RuleParser()
        lines = rp.read_rules(os.path.join("tests","rules1.txt"))
        tokenized = rp.tokenize(lines, lp)

        assert( len(tokenized) == 6 )
        assert( [ t.value for t in tokenized[0] ] == [("A","a1"), "=", ("B","b1")] )
        assert( [ t.value for t in tokenized[1] ] == [("A","a2"), "!=", ("B","b3")] )
        assert( [ t.value for t in tokenized[2] ] == [("A","a2"), "=", [("B","b2"),("C",1.0)]] )
        assert( [ t.value for t in tokenized[3] ] == [[("A","a1"),("B","b2")], "=", [("B","b1"),("C",2)]] )
        assert( [ t.value for t in tokenized[4] ] == [("A","a1","C"), ">", ("B","b2","C")] )
        assert( [ t.value for t in tokenized[5] ] == [("A","a2","C"), "=", ("B","b3","C"), "+", 2] )

        for row in tokenized:
            assert( all( [ t.valid for t in row ] ) )
    
    def test_validate(self):
        lp = LogicPuzzle()
        lp.read_categories( os.path.join("tests", "categories1.txt") )
        lp.create_sets()
        rp = RuleParser()
        lines = rp.read_rules( os.path.join("tests","rules1.txt") )
        tokenized = rp.tokenize(lines, lp)
        validated = rp.validate(tokenized)

        # Validate that the possible rule types are validated
        assert( len(validated) == 6 )
        assert( validated[0][0] == 1 )
        assert( [t.tok_type for t in validated[0][1]] == [TokenType.ELEMENT, TokenType.EQUAL, TokenType.ELEMENT] )
        assert( validated[1][0] == 2 )
        assert( [t.tok_type for t in validated[1][1]] == [TokenType.ELEMENT, TokenType.NOT_EQUAL, TokenType.ELEMENT] )
        assert( validated[2][0] == 3 )
        assert( [t.tok_type for t in validated[2][1]] == [TokenType.ELEMENT, TokenType.EQUAL, TokenType.LIST] )
        assert( validated[3][0] == 4 )
        assert( [t.tok_type for t in validated[3][1]] == [TokenType.LIST, TokenType.EQUAL, TokenType.LIST] )
        assert( validated[4][0] == 5 )
        assert( [t.tok_type for t in validated[4][1]] == [TokenType.PAIR, TokenType.GT, TokenType.PAIR] )
        assert( validated[5][0] == 5 )
        assert( [t.tok_type for t in validated[5][1]] == [TokenType.PAIR, TokenType.EQUAL, TokenType.PAIR, TokenType.PLUS, TokenType.NUMBER] )

        # Deliberately get an invalid token exception
        rp = RuleParser()
        lines = rp.read_rules(os.path.join("tests","invalid_token_rules.txt"))
        tokenized = rp.tokenize(lines, lp)
        try:
            validated = rp.validate(tokenized)
            assert(False)                       # Deliberately fail the test if the except isn't triggered
        except InvalidTokenException as e:
            assert( str(e) == "Expression 4: Invalid token. Token 3 - value = c1" )
        except:
            assert(False)                       # Deliberately fail the test if any other exception is triggered

        # Deliberately get an unexpected token exception
        rp = RuleParser()
        lines = rp.read_rules( os.path.join("tests","unexpected_token_rules.txt") )
        tokenized = rp.tokenize(lines, lp)
        try:
            validated = rp.validate(tokenized)
            assert(False)                       # Deliberately fail the test if the except isn't triggered
        except UnexpectedTokenException as e:
            assert( str(e) == "Expression 3: Unexpected token. Token 2 - value = [('B', 'b2'), ('C', 1.0)], type = TokenType.LIST" )
        except:
            assert(False)                       # Deliberately fail the test if any other exception is triggered

        # Deliberately get a missing token exception
        rp = RuleParser()
        lines = rp.read_rules( os.path.join("tests","missing_token_rules.txt") )
        tokenized = rp.tokenize(lines, lp)
        try:
            validated = rp.validate(tokenized)
            assert(False)                       # Deliberately fail the test if the except isn't triggered
        except MissingTokenException as e:
            assert( str(e) == "Expression 3: Expression ended early. Expected token after '=', type = TokenType.EQUAL" )
        except:
            assert(False)                       # Deliberately fail the test if any other exception is triggered

if __name__ == "__main__":
    unittest.main()