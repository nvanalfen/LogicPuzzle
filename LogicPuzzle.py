# -*- coding: utf-8 -*-
"""
Created on Sat Oct 17 12:31:32 2020

@author: nvana
"""

import pandas as pd
import numpy as np

# CLUE TYPES
# Type 1:       Ai is Bj
# Type 2:       Ai is not Bj
# Type 3:       Ai is Bj or Ck (xor implied)
# Type 4:       each of [list of Ai],
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
            self.categories[label] = np.array( df[label] )
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
    
    # Given an element, return the set that contains the element
    # TODO : I'm not sure about this, I think I made it wrong
    def get_parent_set(self, element):
        for A in self.sets:
            if element in A:
                return A
    
    # Returns the full list of elements to which element belongs
    def get_full_parent_set(self, element):
        for key in self.categories:
            if element in self.categories[key]:
                return self.categories[key]
    
    # Returns the label of the category to which element belongs
    def get_parent_set_category(self, element):
        for key in self.categories:
            if element in self.categories[key]:
                return key
    
    # Unpacks key into cat_A, el_A, cat_B
    def unpack_key(self, key):
        return key[0], key[1], key[2]