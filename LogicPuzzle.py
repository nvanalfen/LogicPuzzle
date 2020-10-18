# -*- coding: utf-8 -*-
"""
Created on Sat Oct 17 12:31:32 2020

@author: nvana
"""

import pandas as pd
import numpy as np

# CLUE TYPES
# Type 1:       Ai is Bj                            # SOLVED - set_element
# Type 2:       Ai is not Bj                        # SOLVED - set_not_element
# Type 3:       Ai is Bj or Ck (xor implied)        # SOLVED - is_one_of
# Type 4:       each of [list of Ai],               # IN PROGRESS
#               is one of [list of A'j]
# Type 5a:      AiB > AjB
# Type 5b:      AiB = AiB + x

# TODO : Perform more thorough tests on multi_is_one_of

# Class to hold a logic puzzle and the functions to solve it
class LogicPuzzle:
    def __init__(self):
        self.categories = {}        # dict from category name to list of elements in that category
        self.sets = {}              # dict from (categor_A_name, element_A_name, category_B_name) to set of elements in category_B that may be linked to element_A from category_A
        self.clues = []             # list of [ clue_function, [args for clue_function], solved ]
        self.solutions = {}         # 
        self.debug_info = None
    
    # SETUP FUNCTIONS - SETS UP THE LOGIC PUZZLE ##############################
        
    # Given a dict of categories, set it as the logic puzzle's
    def set_categories(self, cats):
        self.categories = cats
        self.generate_sets()
    
    # Given a csv file containing the categories (label as header), fill the logic puzzle's categories
    def read_categories(self, f_name):
        df = pd.read_csv(f_name)
        for label in df.columns:
            self.categories[label] = list( df[label] )
        self.generate_sets()
    
    # Generates sets for the given categories
    def generate_sets(self):
        for key_a in self.categories:
            for key_b in self.categories:
                for element in self.categories[key_a]:
                    if not key_a is key_b:
                        self.sets[ (key_a, element, key_b) ] = set( self.categories[key_b] )
    
    def set_clues(self, clues):
        self.clues = clues
    
    def read_clues(self, f_name):
        pass
    
    # CONVENIENCE FUNCTIONS - FOR USE WITHIN THE OTHER FUNCTIONS ##############
    
    # Returns the full set of elements to which element belongs
    def get_full_parent_set(self, element):
        for key in self.categories:
            if element in self.categories[key]:
                return set(self.categories[key])
    
    # Returns the label of the category to which element belongs
    def get_parent_set_category(self, element):
        for key in self.categories:
            if element in self.categories[key]:
                return key
    
    # Unpacks key into cat_A, el_A, cat_B
    def unpack_key(self, key):
        return key[0], key[1], key[2]
    
    # Get the combined lengths of all of the sets
    def get_total_length(self):
        size = 0
        for key in self.sets:
            size += len( self.sets[key] )
        return size
    
    # Puzzle will be solved when all sets have length 1
    def is_solved(self):
        solved = True
        for key in self.sets:
            solved = solved and len(self.sets[key]) == 1
        return solved
    
    # returns the complement of the universal set with set_A
    def complement(self, A_set, universal):
        return universal-A_set

    # Intersects 
    def is_element(self, A_set, element):
        return A_set & set([element])
    
    def exclude_element(self, A_set, element):
        if element in A_set:
            A_set.remove(element)
        return A_set
    
    # CLUE FUNCTIONS - HANDLES THE CLUES THEMSELVES ###########################
    
    # Type 1 clue solution
    def set_element(self, el_A, el_B, inner_call=False):
        category_A = self.get_parent_set_category(el_A)
        category_B = self.get_parent_set_category(el_B)
        all_els_A = self.get_full_parent_set(el_A)           # get all elements of parent set of el_A
        set_A = self.sets[ (category_A, el_A, category_B) ]
        set_A = self.is_element(set_A, el_B)
        self.sets[ (category_A, el_A, category_B) ] = set_A
        
        for el in all_els_A:
            if el != el_A:
                temp_set = self.sets[ (category_A, el, category_B) ]
                temp_set = self.exclude_element(temp_set, el_B)
                self.sets[ (category_A, el, category_B) ] = temp_set
        
        # Because sets are symmetric, if el_A on cat_B is el_B, then el_B on cat_A is el_A
        if not inner_call:
            self.set_element(el_B, el_A, inner_call=True)
        
        return True             # Always return True, this clue has no extra steps
    
    # Type 2 clue solution
    def set_not_element(self, el_A, el_B, inner_call=False):
        category_A = self.get_parent_set_category(el_A)
        category_B = self.get_parent_set_category(el_B)
        set_A = self.sets[ (category_A, el_A, category_B) ]
        set_A = self.exclude_element(set_A, el_B)
        self.sets[ (category_A, el_A, category_B) ] = set_A
        
        if not inner_call:
            self.set_not_element(el_B, el_A, inner_call=True)
    
        return True             # Always return True, this clue has no extra steps
    
    # Type 3 clue solution
    # For clue that says el_A is either el_B or el_C where el_A, el_B, and el_C are
    # members of sets A, B, and C respectively
    def is_one_of(self, el_A, el_B, el_C):
        category_A = self.get_parent_set_category(el_A)
        category_B = self.get_parent_set_category(el_B)
        category_C = self.get_parent_set_category(el_C)
        set_AB = self.sets[ (category_A, el_A, category_B) ]
        set_AC = self.sets[ (category_A, el_A, category_C) ]
        
        self.set_not_element(el_B, el_C)
        
        if len( set_AB & set( [el_B] ) ) == 0:
            return self.set_element(el_A, el_C)
        elif len( set_AC & set( [el_C] ) ) == 0:
            return self.set_element(el_A, el_B)
            
        return False
    
    # Type 4 clue solution
    def multi_is_one_of(self, elements_A, elements_B):
        # Exclude all elements in elements_A from the other elements in elements_A, same for B
        self.mutual_exclude(elements_A)
        self.mutual_exclude(elements_B)
        self.check_single_mapping(elements_A, elements_B)
        pairings = self.pair_categories(elements_A, elements_B)
        
        return self.remove_pairs(elements_A, elements_B, pairings)
    
    # Exclude elements in a list from the sets of the other elements in that list
    def mutual_exclude(self, elements):
        for el_A in elements:
            category_A = self.get_parent_set_category(el_A)
            for el_B in elements:
                category_B = self.get_parent_set_category(el_B)
                if category_A != category_B:
                    set_A = self.sets[ (category_A, el_A, category_B) ]
                    set_A = self.exclude_element(set_A, el_B)
                    self.sets[ (category_A, el_A, category_B) ] = set_A
    
    # Check to see if everything in elements_B belongs to the same set, if so, set
    # the sets of elements_A on category_B to only the elements in elements_B
    def check_single_mapping(self, elements_A, elements_B):
        cats_B = set( [ self.get_parent_set_category(el) for el in elements_B ] )
        if len(cats_B) == 1:
            cat_B = cats_B.pop()
            for el_A in elements_A:
                cat_A = self.get_parent_set_category(el_A)
                set_A = self.sets[ (cat_A, el_A, cat_B) ]
                set_A = set_A & set(elements_B)
                self.sets[ (cat_A, el_A, cat_B) ] = set_A
    
    # Pair any elements in elements_A to those in elements_B when there is enough information
    def pair_categories(self, elements_A, elements_B):
        categories_B = list( set( [ self.get_parent_set_category(el) for el in elements_B ] ) )
        pairings = []
        for el_A in elements_A:
            category_A = self.get_parent_set_category(el_A)
            for cat in categories_B:
                if cat != category_A:
                    #universal = all_sets[ (category_A, el_A, cat) ]    # TODO make sure this is the right universal set
                    universal = set( [ i for i in elements_B if i in self.categories[cat] ] )
                    seed_set = set()
                    # yes, elements_A, not B, look at others in the same list
                    for el_B in elements_A:
                        if el_A != el_B:
                            category_B = self.get_parent_set_category(el_B)
                            if category_B != cat:
                                seed_set = seed_set | self.sets[ (category_B, el_B, cat) ]

                    seed_set = self.complement(seed_set, universal)
                    set_A = self.sets[ (category_A, el_A, cat) ]
                    res = set_A & seed_set
                    
                    # If the resulting set is empty, there aren't enough constraints to specify
                    if len(res) != 0:
                        self.sets[ (category_A, el_A, cat) ] = set(res)       # Should this be inside the len == 1?
                        if len(res) == 1:
                            pairings.append( (el_A, res.pop()) )
        
        return pairings
    
    # If there are pairs, remove them from elements_A and elements_B (we don't need to solve them again)
    # If elements_A and elements_B are emptied, the clue is fully solved
    def remove_pairs(self, elements_A, elements_B, pairings):
        for pair in pairings:
            elements_A.remove( pair[0] )
            elements_B.remove( pair[1] )
        if len(elements_A) == 0 and len(elements_B) == 0:
            return True
        elif len(elements_A) == 1 and len(elements_B) == 1:
            el_A = elements_A.pop()
            el_B = elements_B.pop()
            cat_A = self.get_parent_set_category(el_A)
            cat_B = self.get_parent_set_category(el_B)
            set_A = self.sets[ (cat_A, el_A, cat_B) ]
            set_A = self.is_element(set_A, el_B)
            self.sets[ (cat_A, el_A, cat_B) ] = set_A
            return True
        return False
    
    # Type 5a and 5b clue solution
    # With elements el_A and el_B belonging to sets A and B respectively (A and B may be the same),
    # with another set C different from A and B containing numerical values,
    # knowing that the final element of set el_A on C is greater than the 
    # final element of set el_B on C,
    # narrows down the remaining possibilities of el_A on C and el_B on C
    # if no value is given, we only know that the final element of el_A on C is greater than
    # the final element of el_B on C
    def greater_than(self, el_A, el_B, category, value=None):
        # el_A and el_B in separate categories => exclude a and b from each other
        category_A = self.get_parent_set_category(el_A)
        category_B = self.get_parent_set_category(el_B)
        set_A = self.sets[ (category_A, el_A, category) ]
        set_B = self.sets[ (category_B, el_B, category) ]
        
        # If el_A on category is greater than el_B on category and they are not in the same category
        # then el_A on B does not include el_B and el_B on A does not include el_A
        if category_A != category_B:
            self.set_not_element(el_A, el_B)
            
        if value is None:
            set_A = set( [ s for s in set_A if s > min(set_B) ] )
            set_B = set( [ s for s in set_B if s < max(set_A) ] )
        else:
            set_A = set_A & set( [ s+value for s in set_B ] )
            set_B = set_B & set( [ s-value for s in set_A ] )
        
        self.sets[ (category_A, el_A, category) ] = set_A
        self.sets[ (category_B, el_B, category) ] = set_B
        self.return_exclusion(category_A, el_A, category)
        self.return_exclusion(category_B, el_B, category)
        
        if len(set_A) == 1 or len(set_B) == 1:
            return True     # This clue can give no more information
        return False        # There is still information to be gained
    
    # OTHER LOGIC FUNCTIONS - IN ADDITION TO THE CLUES, USE LOGIC TO DRAW CONCLUSIONS
    
    def return_exclusion_all(self):
        for cat_A in self.categories:
            for el_A in self.categories[cat_A]:
                for cat_B in self.categories:
                    if cat_A != cat_B:
                        self.return_exclusion(cat_A, el_A, cat_B)
    
    # If (cat_A, el_A, cat_B) does not contain element el_B1, then (cat_B, el_B1, cat_A) cannot contain el_A
    # Remove el_A from the sets of the elements not included in el_A's set
    def return_exclusion(self, cat_A, el_A, cat_B):
        for el_B in self.complement( self.sets[ (cat_A, el_A, cat_B) ], set(self.categories[cat_B]) ):
            self.set_not_element(el_B, el_A)
            
    # Because the sets are symmetric, for any set element_A on category_B with only one element_B,
    # element_A should be the only element of the set element_B on category_A
    def symmetrize(self):
        for key in self.sets:
            if len( self.sets[ key ] ) == 1:
                # For solved sets, make sure the relationship is reciprocated
                cat_A, el_A, cat_B = self.unpack_key(key)
                el_B = None
                for el in self.sets[key]:
                    el_B = el
                
                self.set_element(el_B, el_A)
    
    # Applies the transitive relationship. If A is B and B is C, the A is C
    # Also, if A is B and B is not C, A is not C
    def chain_relation(self):
        for key in self.sets:
            if len( self.sets[key] ) == 1:
                cat_A, el_A, cat_B = self.unpack_key(key)
                el_B = None
                for el in self.sets[key]:
                    el_B = el
                    
                for cat in self.categories:
                    if cat != cat_A and cat != cat_B:
                        combo = self.sets[(cat_A, el_A, cat)] & self.sets[(cat_B, el_B, cat)]
                        self.sets[(cat_A, el_A, cat)] = set(combo)
                        self.sets[(cat_B, el_B, cat)] = set(combo)
                        #set_B = self.sets[ (cat_B, el_B, cat) ]
                        # If we know it is another element, link el_A to that element
                        #if len(set_B) == 1:
                        #    self.chain_include(el_A, set_B)
                        #else:
                            # Make sure all negative relationships are reciprocated
                        #    self.chain_exclude(el_A, cat_B, set_B)
    
    # If el_A links to el_B, and el_B links to el_C, link el_A to el_C
    def chain_include(self, el_A, set_B):
        el_C = None
        for el in set_B:
            el_C = el
        self.set_element(el_A, el_C)
    
    # If el_A links to el_B, and el_B cannot be certain elements els_C, then el_A cannot be those els_C either
    def chain_exclude(self, el_A, cat_B, set_B):
        for el in self.complement( set_B, set(self.categories[cat_B]) ):
            self.set_not_element(el_A, el)          # Not in set_B, so can't link to el_A
    
    # if n sets from a category have the same n elements, then the remaining sets cannot have those
    # n elements
    def n_of_n(self):
        cats = list( self.categories.keys() )
        for cat_A in cats:
            for cat_B in cats:
                if cat_A != cat_B:
                    for el_AA in self.categories[cat_A]:
                        set_A = self.sets[ (cat_A, el_AA, cat_B) ]
                        same = [el_AA]
                        for el_AB in self.categories[cat_A]:
                            if el_AA != el_AB and self.sets[ (cat_A, el_AB, cat_B) ] == set_A:
                                same.append(el_AB)
                        
                        # n sets of n elements but not just all of the possibilities
                        if len(same) != len(self.categories) and len(same) == len(set_A):
                            self.exclude_n_of_n(same, set_A, cat_A, cat_B)
    
    def exclude_n_of_n(self, same_sets, elements, cat_A, cat_B):
        for el_A in self.categories[cat_A]:
            if not el_A in same_sets:
                for el_B in elements:
                    self.set_not_element(el_A, el_B)
    
    # SOLUTION FUNCTIONS ######################################################
            
    # TODO : multi_is_one_of is setting some sets to empty sets. Track through and see where this happens
    # A.txt gives all sets before the problem loop, clue_2.txt gives all the sets after multi_is_one_of runs
    def solve(self, f_name="Output.txt"):
        
        change = 1
        while change:
            print("Loop")
            before = self.get_total_length()
            
            self.solve_clues()

            self.symmetrize()                   #
            self.chain_relation()               #
            self.return_exclusion_all()         #
            self.n_of_n()

            after = self.get_total_length()
            change = before - after
        
        if self.is_solved():
            self.set_solutions()
            self.write_solutions(f_name)
    
    # Iterate through the clues and solve each one that's not already solved
    def solve_clues(self):
        
        for clue in self.clues:
            if not clue[-1]:
                func = clue[0]
                args = clue[1]
                res = func( *args )
                clue[-1] = res
    
    def set_solutions(self):
        if not self.is_solved():
            return
        primary_category = list(self.categories.keys())[0]
        self.solutions = {}
        for el in self.categories[primary_category]:
            self.solutions[el] = []
        
        for cat in self.categories.keys():
            if cat != primary_category:
                for key in self.solutions:
                    self.solutions[key].append( list( self.sets[(primary_category, key, cat)] )[0] )
                    
    def write_solutions(self, f_name):
        file = open(f_name, "w")
        for key in self.solutions:
            file.write( str(key) )
            file.write( " :\t" )
            file.write( str(self.solutions[key]) )
            file.write("\n")
        file.close()
    
    def contains_null(self):
        for key in self.sets:
            if len(self.sets[key]) == 0:
                return True
        return False

def test():
    a = LogicPuzzle()
    a.read_categories("Book1.csv")
    a.clues.append( [ a.set_element, ["Pam Powell", "juicer"], False ] )
    a.clues.append( [ a.set_element, [500, "blu-ray"], False ] )
    a.clues.append( [ a.multi_is_one_of, [ ["Mitch Mayo", "juicer"], [475, 450] ], False ] )
    a.clues.append( [ a.is_one_of, [ "Kit Kelley", "juicer", 400 ], False ] )
    a.clues.append( [ a.is_one_of, [ "Ned Norris", "blender", 475 ], False ] )
    a.clues.append( [ a.set_not_element, [ 475, "planter" ], False ] )
    a.clues.append( [ a.greater_than, [ "Mitch Mayo", "blender", "Prices", 50 ], False ] )
    
    a.solve()
    return a

def test2():
    a = LogicPuzzle()
    a.read_categories("Book2.csv")
    a.clues.append( [ a.is_one_of, [12, 33, "Lois"], False ] )
    a.clues.append( [ a.set_not_element, [30, 10], False ] )
    a.clues.append( [ a.set_not_element, ["Dublin", 12], False ] )
    a.clues.append( [ a.set_not_element, ["Dublin", "Marie"], False ] )
    a.clues.append( [ a.set_not_element, [12, "Marie"], False ] )
    a.clues.append( [ a.set_not_element, ["Lois", "Boston"], False ] )
    a.clues.append( [ a.set_element, [ 33, 2 ], False ] )
    a.clues.append( [ a.greater_than, [ 10, "Los Angeles", "Wins" ], False ] )
    a.clues.append( [ a.multi_is_one_of, [ ["Glasgow", 12], ["Annie", 36] ], False  ] )
    a.clues.append( [ a.set_element, [ "Marie", 2 ], False ] )
    a.clues.append( [ a.greater_than, [ "Gina", 4, "Wins", 3 ], False ] )
    
    a.solve()
    return a

# Debug functionto see the sets
def write(data, f_name):
    file = open(f_name, "w")
    for key in data:
        file.write(str(key))
        file.write("\t")
        file.write(str(data[key]))
        file.write("\n")
    file.close()
    
def write2(data, f_name):
    file = open(f_name, "w")
    file.write(str(data))
    file.close()