import numpy as np
import pandas as pd

class LogcPuzzle:
    def __init__(self, category_f_name=None, rule_f_name=None):
        self.categories = []                # list of category titles, first title will be the key category
        self.category_values = {}           # dict from category name to set of values in that category
        self.full_sets = {}                 # dict from (category_A_name, category_A_value) to set of remaining category_B_values

        if not category_f_name is None:
            self.read_categories(category_f_name)
        if not rule_f_name is None:
            self.read_rules(rule_f_name)
    
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