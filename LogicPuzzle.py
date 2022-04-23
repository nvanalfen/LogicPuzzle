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
                self.categories.append( title )
                self.category_values[ title ]= values
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

    def peek(a):
        val = a.pop()
        a.add(val)
        return val
    
    ##### Rule Functions ###############################################################################################################

    def a_is_b(self, cat_A, el_A, cat_B, el_B, inner=False):
        self.full_sets[ (cat_A, el_A, cat_B) ] = set([el_B])
        for val in self.category_values[cat_A]:
            if val != cat_A:
                pass

    ##### General Logic Functions ######################################################################################################