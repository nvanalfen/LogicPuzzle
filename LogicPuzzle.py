import numpy as np
import pandas as pd

class LogicPuzzle:
    def __init__(self, category_f_name=None, rule_f_name=None):
        self.categories = []                # list of category titles, first title will be the key category
        self.category_values = {}           # dict from category name to set of values in that category
        self.full_sets = {}                 # dict from (category_A_name, category_A_value, category_B_name) to set of remaining category_B_values

        if not category_f_name is None:
            self.read_categories(category_f_name)
        if not rule_f_name is None:
            self.read_rules(rule_f_name)
        
        self.create_sets()
    
    ##### Setup Functions ##############################################################################################################

    def read_categories(self, f_name):
        try:
            f = open(f_name)
            for line in f:
                row = line.split(":")
                title = row[0].strip()
                values = set( [ val.strip() for val in row[1].split(",") ] )

                # Try to cast values to float, otherwise stay categorical
                try:
                    temp = set( [ float(val) for val in values ] )
                    values = temp
                except:
                    pass

                self.categories.append( title )
                self.category_values[ title ] = values
            
            f.close()
        except:
            print("Error")

    def read_rules(self, f_name):
        pass

    def create_sets(self):
        for i in range(len(self.categories)):
            cat_A = self.categories[i]
            for j in range(len(self.categories))[i+1:]:
                cat_B = self.categories[j]
                for val in self.category_values[ cat_A ]:
                    self.full_sets[ ( cat_A, val, cat_B ) ] = self.category_values[ cat_B ]
                for val in self.category_values[ cat_B ]:
                    self.full_sets[ ( cat_B, val, cat_A ) ] = self.category_values[ cat_A ]
    
    ##### Auxilliary Functions #########################################################################################################

    # Check the first element of a set (useful when the cardinality of a is 1)
    def peek(a):
        val = a.pop()
        a.add(val)
        return val
    
    # Returns a subset of a where each element is larger than min(b), and subset of b where each element is less that max(a)
    # If val is not None, return a intersect (b + val) and b intersect (a - val)
    def subset(a, b, val=None):
        if val is None:
            sub_a = set( [ x for x in a if x > min(b) ] )
            sub_b = set( [ x for x in b if x < max(a) ] )
        else:
            sub_a = a & set( [ x+val for x in b ] )
            sub_b = b & set( [ x-val for x in a ] )
        
        return sub_a, sub_b

    # Checks the completion of the puzzle
    def is_complete(self):
        return all( [ len( self.full_sets[key] ) == 1 for key in self.full_sets ] )
    
    ##### Rule Functions ###############################################################################################################

    # Rule types:
    # 1)    a is b          -> Clear-cut, we are told el_A from cat_A is linked to el_B from cat_B
    #                       -> (cat_A, el_A, cat_B) = {el_B}
    #                       -> (cat_B, el_B, cat_A) = {el_A}
    #                       -> run (c is not b) for all c != a,b
    #                       -> run (c is not a) for all c != a,b
    # 2)    a is not b      -> Clear-cut, remove el_B of cat_B from possibilities of el_A from cat_A
    #                       -> (cat_A, el_A, cat_B) -= {el_B}
    #                       -> (cat_B, el_B, cat_A) -= {el_A}
    # 3)    a is b or c     -> Run (b is not c) and (c is not b)
    #                       -> If cat_B == cat_C, (cat_A, el_A, cat_B) = { el_B, el_C }
    #                       -> If (cat_A, el_A, cat_B) does not contain el_B, set to el_C
    #                       -> If (cat_A, el_A, cat_C) does not contain el_C, set to el_B
    # 4)    [N*] = [M*]     -> Each of the N elements (in N*), from possibly different categories, can be one of the N elements in [M*]
    #                       -> Run (N1 is not Ni) for Ni != N1 in N*
    #                       -> Run (M1 is not Mi) for Mi != M1 in M*
    #                       -> Generate { (cat_M, el_M) } from union of ( (cat_N, el_N, cat_M) intersect {el_M} ) for all N in N*, M in M*
    #                       -> If cardinality is 1, run el_N is el_M
    #                       -> Generate { (cat_N, el_N) } from union of ( (cat_M, el_M, cat_N) intersect {el_N} ) for all N in N*, M in M*
    #                       -> If cardinality is 1, run el_N is el_M
    # 5a)   a > b           -> We are told (cat_A, el_A, cat_C) > (cat_B, el_B, cat_C)
    #                       -> run (a is not b)
    #                       -> run (b is not a)
    #                       -> (cat_A, el_A, cat_C) = (cat_A, el_A, cat_C) > min( (cat_B, el_B, cat_C) )
    #                       -> (cat_B, el_B, cat_C) = (cat_B, el_B, cat_C) < max( (cat_A, el_A, cat_C) )
    # 5b)   a = b + x       -> We are told (cat_A, el_A, cat_C) is x greater than (cat_B, el_B, cat_C)
    #                       -> run (a is not b)
    #                       -> run (b is not a)
    #                       -> (cat_A, el_A, cat_C) = (cat_A, el_A, cat_C) intersect ( (cat_B, el_B, cat_C) + x )
    #                       -> (cat_B, el_B, cat_C) = (cat_B, el_B, cat_C) intersect ( (cat_A, el_A, cat_C) - x )

    def a_is_b(self, cat_A, el_A, cat_B, el_B, inner=False):
        self.full_sets[ (cat_A, el_A, cat_B) ] = set([el_B])
        for val in self.category_values[cat_A]:
            if val != el_A:
                self.a_is_not_b(cat_A, val, cat_B, el_B)
        
        # Apply the reverse, set inner to True so the recursion ends
        if not inner:
            self.a_is_b(cat_B, el_B, cat_A, el_A, inner=True)
    
    def a_is_not_b(self, cat_A, el_A, cat_B, el_B):
        self.full_sets[ (cat_A, el_A, cat_B) ] -= set([el_B])

    ##### General Logic Functions ######################################################################################################