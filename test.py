import unittest
from LogicPuzzle import LogicPuzzle
import os

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
        pass

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

if __name__ == "__main__":
    unittest.main()