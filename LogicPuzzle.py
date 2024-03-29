import numpy as np
from prettytable import PrettyTable
import pandas as pd
from RuleParser import RuleParser, InvalidTokenException, UnexpectedTokenException, MissingTokenException
from Token import TokenType
import itertools

class LogicPuzzle:
    def __init__(self, category_f_name=None, rule_f_name=None):
        self.categories = []                # list of category titles, first title will be the key category
        self.category_values = {}           # dict from category name to set of values in that category
        self.full_sets = {}                 # dict from (category_A_name, category_A_value, category_B_name) to set of remaining category_B_values
        self.parser = RuleParser()          # parser to tokenize, and validate rules
        self.rule_f_name = rule_f_name      # File where the rules are stored
        self.rules = []                     # list of rules. Each rule is a tuple of (function, parameters)
        self.key_category = None

        if not category_f_name is None:
            self.read_categories(category_f_name)
        if not rule_f_name is None:
            self.read_rules()
        
        self.create_sets()
    
    ##### Setup Functions ##############################################################################################################

    def read_categories(self, category_f_name):
        try:
            lines = []
            f = open(category_f_name)
            for line in f:
                lines.append(line)
            
            f.close()
            self.set_categories(lines)
        except:
            print("Error")

    def set_categories(self, lines):
        for line in lines:
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
            if self.key_category is None:
                self.key_category = title

    def read_rules(self):
        if self.rule_f_name is None:
            return

        validated_rules = self.parser.get_validated_rules(self.rule_f_name, self)
        self.set_rules(validated_rules)

    # Given the validated tokens, build the list of functions calls and parameters to be called each loop
    def set_rules(self, validated):
        rule_dict = {}
        rule_dict[1] = self.a_is_b
        rule_dict[2] = self.a_is_not_b
        rule_dict[3] = self.one_to_many
        rule_dict[4] = self.many_to_many
        rule_dict[5] = self.a_greater_than_b
        rule_dict[6] = self.multi_exclusion             # Not fully a rule, just a shorthand for multiple a_is_not_many calls

        for line in validated:
            ind, args = line
            args = self.extract_params(args)
            self.rules.append( ( rule_dict[ind], args ) )

    # Take the tokens and pull out the values that will be the parameters
    def extract_params(self, line):
        params = []
        cat_C = None
        numerical = None
        for tok in line:
            if tok.tok_type == TokenType.ELEMENT:
                params.extend( tok.value )
            elif tok.tok_type == TokenType.LIST:
                params.append( tok.value )
            elif tok.tok_type == TokenType.PAIR:
                params.extend( tok.value[:2] )
                cat_C = tok.value[2]
            elif tok.tok_type == TokenType.NUMBER:
                numerical = tok.value

        if not cat_C is None:
            params.append( cat_C )
        if not numerical is None:
            params.append( numerical )

        return params

    # Create the initial sets
    def create_sets(self):
        for i in range(len(self.categories)):
            cat_A = self.categories[i]
            for j in range(len(self.categories))[i+1:]:
                cat_B = self.categories[j]
                for val in self.category_values[ cat_A ]:
                    self.full_sets[ ( cat_A, val, cat_B ) ] = set( self.category_values[ cat_B ] )
                for val in self.category_values[ cat_B ]:
                    self.full_sets[ ( cat_B, val, cat_A ) ] = set( self.category_values[ cat_A ] )

    ##### Auxilliary Functions #########################################################################################################

    def clone_sets(self):
        clone = {}
        for key in self.full_sets:
            clone[key] = set(self.full_sets[key])
        return clone

    def contains_empty_sets(self):
        for key in self.full_sets:
            if self.full_sets[key] == set():
                return True
        return False

    # Check the first element of a set (useful when the cardinality of a is 1)
    def peek(a):
        val = a.pop()
        a.add(val)
        return val
    
    # Returns a subset of a where each element is larger than min(b), and subset of b where each element is less that max(a)
    # If val is not None, return a intersect (b + val) and b intersect (a - val)
    def subset(self, a, b, val=None):
        if val is None:
            sub_a = set( [ x for x in a if x > min(b) ] )
            sub_b = set( [ x for x in b if x < max(a) ] )
        else:
            sub_a = a & set( [ x+val for x in b ] )
            sub_b = b & set( [ x-val for x in a ] )
        
        return sub_a, sub_b
    
    # Checks how many elements of M_star map to a given category
    def get_possible_M_star(self, cat_A, el_A, M_star):
        possible = []
        for cat_B, el_B in M_star:
            if (cat_A, el_A, cat_B) in self.full_sets and el_B in self.full_sets[ (cat_A, el_A, cat_B) ]:
                possible.append( (cat_B, el_B) )
        return possible

    # Given a (cat_A, el_A) element and a list (M_star) of (cat_B, el_B), if every element in the list belongs to the 
    # same category as the other elements, reduce the set of cat_A, el_A on that category to a set of
    # the elements in that list intersected with the possible elements left for cat_A, el_A on that set
    def check_single_category_list(self, cat_A, el_A, M_star:list) -> None:
        cats = set()
        els = set()
        for cat_B, el_B in M_star:
            cats.add(cat_B)
            els.add(el_B)
        if len(cats) == 1:
            cat_B = cats.pop()
            # Intersect the current set of possibilities with the elements proposed
            self.full_sets[(cat_A, el_A, cat_B)] &= els

            # If there's only one element left, run a_is_b
            # Even though this set is already correct, this call will exclude el_A from the remaining elements
            if len(self.full_sets[(cat_A, el_A, cat_B)]) == 1:
                for el in els:
                    if not el in self.full_sets[(cat_A, el_A, cat_B)]:
                        self.a_is_not_b(cat_A, el_A, cat_B, el)
    
    # Given a list of (cat, el) elements, exclude each (cat_A, el_A) from all other (cat_B, el_B) elements in that list
    def multi_exclusion(self, N_star:list) -> None:
        for cat_B, el_B in N_star:
            for cat_C, el_C in N_star:
                if (cat_B, el_B) != (cat_C, el_C):
                    self.a_is_not_b(cat_B, el_B, cat_C, el_C)
    
    # Check how many of the elements in M_star can still be mapped to (cat_A, el_A)
    # If only one works, set it
    def check_possibilities(self, cat_A, el_A , M_star:list) -> None:
        possible_M_star = self.get_possible_M_star(cat_A, el_A, M_star)
        if len(possible_M_star) == 1:
            cat_B, el_B = possible_M_star[0]
            self.a_is_b(cat_A, el_A, cat_B, el_B)

    # Checks the completion of the puzzle
    def is_complete(self):
        if len( self.full_sets ) == 0:
            return False
        return all( [ len( self.full_sets[key] ) == 1 for key in self.full_sets ] )
    
    ##### Rule Functions ###############################################################################################################

    # Rule types:
    # 1)    a is b              -> Clear-cut, we are told el_A from cat_A is linked to el_B from cat_B
    #                           -> (cat_A, el_A, cat_B) = {el_B}
    #                           -> (cat_B, el_B, cat_A) = {el_A}
    #                           -> run (c is not b) for all c != a,b
    #                           -> run (c is not a) for all c != a,b
    # 2)    a is not b          -> Clear-cut, remove el_B of cat_B from possibilities of el_A from cat_A
    #                           -> (cat_A, el_A, cat_B) -= {el_B}
    #                           -> (cat_B, el_B, cat_A) -= {el_A}
    # 3)    a is one of [M*]    -> Run (b is not c) for all b,c in M*
    #                           -> If cat_B == cat_C for all b,c in M*, (cat_A, el_A, cat_B) = { al el in M* }
    #                           -> Generate { (cat_M, el_M) } from union of ( (cat_A, el_a, cat_M) intersect {el_M} ) for all M in M*
    #                           -> If cardinality is 1, run (a in el_M)
    # 4)    [N*] = [M*]         -> Each of the N elements (in N*), from possibly different categories, can be one of the M elements in [M*]
    #                           -> Run (N1 is not Ni) for Ni != N1 in N*
    #                           -> Run (M1 is not Mi) for Mi != M1 in M*
    #                           -> Generate { (cat_M, el_M) } from union of ( (cat_N, el_N, cat_M) intersect {el_M} ) for all N in N*, M in M*
    #                           -> If cardinality is 1, run el_N is el_M
    #                           -> Generate { (cat_N, el_N) } from union of ( (cat_M, el_M, cat_N) intersect {el_N} ) for all N in N*, M in M*
    #                           -> If cardinality is 1, run el_N is el_M
    # 5a)   a > b               -> We are told (cat_A, el_A, cat_C) > (cat_B, el_B, cat_C)
    #                           -> run (a is not b)
    #                           -> run (b is not a)
    #                           -> (cat_A, el_A, cat_C) = (cat_A, el_A, cat_C) > min( (cat_B, el_B, cat_C) )
    #                           -> (cat_B, el_B, cat_C) = (cat_B, el_B, cat_C) < max( (cat_A, el_A, cat_C) )
    # 5b)   a = b + x           -> We are told (cat_A, el_A, cat_C) is x greater than (cat_B, el_B, cat_C)
    #                           -> run (a is not b)
    #                           -> run (b is not a)
    #                           -> (cat_A, el_A, cat_C) = (cat_A, el_A, cat_C) intersect ( (cat_B, el_B, cat_C) + x )
    #                           -> (cat_B, el_B, cat_C) = (cat_B, el_B, cat_C) intersect ( (cat_A, el_A, cat_C) - x )

    # Rule 1
    def a_is_b(self, cat_A, el_A, cat_B, el_B, inner=False):
        if not (cat_A, el_A, cat_B) in self.full_sets:
            return

        self.full_sets[ (cat_A, el_A, cat_B) ] = set([el_B])
        for val in self.category_values[cat_A]:
            if val != el_A:
                self.a_is_not_b(cat_A, val, cat_B, el_B)
        
        # Apply the reverse, set inner to True so the recursion ends
        if not inner:
            self.a_is_b(cat_B, el_B, cat_A, el_A, inner=True)
    
    # Rule 2
    def a_is_not_b(self, cat_A, el_A, cat_B, el_B, inner=False):
        if not (cat_A, el_A, cat_B) in self.full_sets:
            return
            
        self.full_sets[ (cat_A, el_A, cat_B) ] -= set([el_B])

        if not inner:
            self.a_is_not_b(cat_B, el_B, cat_A, el_A, inner=True)

    # Rule 3
    def one_to_many(self, cat_A, el_A, M_star:list) -> None:
        # Make sure cat_A, el_A can actually map to all cat_B in M_star
        for cat_B, el_B in M_star:
            if not (cat_A, el_A, cat_B) in self.full_sets:
                return

        # Elements in the same list cannot be each other
        self.multi_exclusion(M_star)
        
        # Account for the case that all elements in M_star belong to the same category
        self.check_single_category_list(cat_A, el_A, M_star)

        # Check how many elements in M_star can possible be linked to (cat_A, el_A)
        # If this set is only one element, set it
        # Unfortunately, this will be redundant in the case than all categories are the same (since check_single_category has been run)
        self.check_possibilities(cat_A, el_A, M_star)

        self.reflexive_inclusion()
        self.reflexive_exclusion()
    
    # Rule 4
    # Given a list of (category, element) tuples (N_star), and a similar list for M_star
    def many_to_many(self, N_star, M_star, inner=False):
        # Elements in the same list cannot be each other
        for cat_A, el_A in N_star:
            self.one_to_many(cat_A, el_A, M_star)

        if not inner:
            self.many_to_many(M_star, N_star, inner=True)

    # Rule 5
    # This should cover both cases
    # Assuming (cat_A, el_A, cat_C) is the set said to be larger than (cat_B, el_B, cat_C)
    def a_greater_than_b(self, cat_A, el_A, cat_B, el_B, cat_C, val=None):
        self.a_is_not_b(cat_A, el_A, cat_B, el_B)
        sub_a, sub_b = self.subset( self.full_sets[ (cat_A, el_A, cat_C) ], 
                                    self.full_sets[ (cat_B, el_B, cat_C) ], 
                                    val=val )
        self.full_sets[ (cat_A, el_A, cat_C) ] = sub_a
        self.full_sets[ (cat_B, el_B, cat_C) ] = sub_b

        self.reflexive_inclusion()
        self.reflexive_exclusion()

    ##### General Logic Functions ######################################################################################################

    # Run all the loaded rules
    def rule_sweep(self, intermediate_logic=True):
        for func, params in self.rules:
            func(*params)

            if intermediate_logic:
                # Run logic between each evaluation of rules
                self.logic_sweep()

    # Run all logic functions
    def logic_sweep(self):
        self.reflexive_inclusion()
        self.reflexive_exclusion()
        self.link_inclusion()
        self.link_exclusion()
        self.n_of_n()

    # If (cat_A, el_A, cat_B) = el_B, then (cat_B, el_B, cat_A) = el_A
    def reflexive_inclusion(self):

        for cat_A, el_A, cat_B in self.full_sets:
            els = self.full_sets[(cat_A, el_A, cat_B)]

            # If the set of possibilities is only one element long, it is solved and that element must also
            # have a reflexive relation back on el_A
            if len(els) == 1:
                el_B = LogicPuzzle.peek(els)
                self.a_is_b(cat_B, el_B, cat_A, el_A)
    
    # If (cat_A, el_A, cat_B) can't be el_B, that means (cat_B, el_B, cat_A) can't be el_A
    def reflexive_exclusion(self):

        for cat_A, el_A, cat_B in self.full_sets:
            els = self.full_sets[(cat_A, el_A, cat_B)]
            universal = self.category_values[cat_B]             # All the possible values in cat_B
            excluded = universal - els                          # The elements in cat_B that are no longer possibly linked to el_B
            
            for el_B in excluded:
                self.a_is_not_b(cat_B, el_B, cat_A, el_A)
    
    # If (cat_A, el_A, cat_B) = el_B, and (cat_B, el_B, cat_C) = el_C, then (cat_A, el_A, cat_C) = el_C
    # A broader way of characterizing this is:
    # (cat_A, el_A, cat_C) = (cat_A, el_A, cat_C) intersect ( set() union (cat_B, el_B, cat_C) union ... )
    # for all el_B in (cat_A, el_A, cat_B)
    def link_inclusion(self):
        
        for cat_A, cat_B, cat_C in itertools.permutations(self.categories,3):
            for el_A in self.category_values[cat_A]:
                seed = set()
                for el_B in self.full_sets[(cat_A, el_A, cat_B)]:
                    seed |= self.full_sets[(cat_B, el_B, cat_C)]
                self.full_sets[(cat_A, el_A, cat_C)] &= seed
                        
    # If el_B is not in (cat_A, el_A, cat_B), and (cat_B, el_B, cat_C) = el_C
    # then (cat_A, el_A, cat_C) -= (cat_B_, el_B, cat_C)
    def link_exclusion(self):
        
        for cat_A, cat_B, cat_C in itertools.permutations(self.categories,3):
            universal_B = self.category_values[cat_B]
            for el_A in self.category_values[cat_A]:
                for el_B in (universal_B - self.full_sets[(cat_A, el_A, cat_B)]):
                    c_set = self.full_sets[(cat_B, el_B, cat_C)]
                    if len(c_set) == 1:
                        # If A,a1 is not B,b1, but we know B,b1 is C,c1, then we know A,a1 cannot be C,c1
                        self.full_sets[(cat_A, el_A, cat_C)] -= c_set

    # If n (of el_A) sets in (cat_A, el_A, cat_B) have the same n values, then exclude those n values from the remaining el_A values
    def n_of_n(self):
        for cat_A, cat_B in itertools.permutations(self.categories,2):
            max_els = len( self.category_values[cat_B] )
            n_sets = {}
            for el_A in self.category_values[cat_A]:
                key = (cat_A,el_A,cat_B)
                temp = tuple(self.full_sets[key])
                if len(temp) == max_els:
                    continue
                if not temp in n_sets:
                    n_sets[temp] = set( self.category_values[cat_A] )
                
                n_sets[temp].remove( el_A )

            for element_set in n_sets:
                key_sets = n_sets[element_set]
                if len(key_sets) == max_els - len(element_set):
                    for el_A in key_sets:
                        for el_B in element_set:
                            #print( " - ".join([str(cat_A), str(el_A), str(cat_B), str(el_B)]) )
                            self.a_is_not_b(cat_A, el_A, cat_B, el_B)
    
    ##### GAMEPLAY #####################################################################################################################

    def solve(self, intermediate_logic=True, show=True, return_results=False):
        changed = True
        sweeps = 0

        while changed:
            prev = self.clone_sets()
            self.rule_sweep(intermediate_logic)
            if not intermediate_logic:
                self.logic_sweep()                      # No need to do this if I'm running it after each rule
            changed = ( prev != self.full_sets )
            sweeps += 1
            if self.is_complete():
                break
        
        if show:
            print("Iterations: ",sweeps)
            if self.is_complete():
                print("Solved!")
                self.show_grid()
            else:
                print("Not solved...")

        if return_results:
            return self.is_complete(), sweeps, self.get_printable_grid()

    def get_grid(self, separate_title=False):
        if self.key_category is None:
            return
        
        titles = [self.key_category]
        for title in self.categories:
            if title != self.key_category:
                titles.append( title )
        
        data = [ [ str(val) for val in self.category_values[self.key_category] ] ]
        for category in titles[1:]:
            row = []
            for key_element in self.category_values[self.key_category]:
                res = self.full_sets[(self.key_category, key_element, category)]
                if len(res) == 1:
                    row.append( str( LogicPuzzle.peek(res) ) )
                else:
                    row.append( "" )
            data.append(row)
        
        data = np.array(data).T
        if separate_title:
            return titles, data
        return np.vstack([title,data])

    def get_printable_grid(self):
        titles, data = self.get_grid(separate_title=True)
        tab = PrettyTable(titles)
        for row in data:
            tab.add_row(row)
        return tab

    def show_grid(self):
        tab = self.get_printable_grid()
        print(tab)