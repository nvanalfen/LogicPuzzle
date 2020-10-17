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

# Class to hold a logic puzzle and the functions to solve it
class LogicPuzzle:
    def __init__(self):
        self.categories = {}        # dict from category name to list of elements in that category
        self.sets = {}              # dict from (categor_A_name, element_A_name, category_B_name) to set of elements in category_B that may be linked to element_A from category_A
        self.clues = []             # list of ( clue_function, [args for clue_function] )
    
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
    
    # If (cat_A, el_A, cat_B) does not contain element el_B1, then (cat_B, el_B1, cat_A) cannot contain el_A
    # Remove el_A from the sets of the elements not included in el_A's set
    def return_exclusion(self, cat_A, el_A, cat_B):
        for el_B in self.complement( self.sets[ (cat_A, el_A, cat_B) ], set(self.categories[cat_B]) ):
            self.set_not_element(el_B, el_A)