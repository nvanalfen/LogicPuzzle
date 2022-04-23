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
        pass

    ##### Test Rule Functions ######################################################################################################

    ##### Test Auxilliary Funcitons ################################################################################################

if __name__ == "__main__":
    unittest.main()