# -*- coding: utf-8 -*-
"""
Created on Thu Sep 10 18:18:12 2020

@author: nvana
"""

# CLUE TYPES
# Type 1:       Ai is Bj                            SOLVED - set_element
# Type 2:       Ai is not Bj                        SOLVED - set_not_element
# Type 3:       Ai is Bj or Ck (xor implied)        SOLVED - is_one_of
# Type 4:       each of [list of Ai],
#               is one of [list of A'j]
# Type 5a:      AiB > AjB                           SOLVED - greater_than
# Type 5b:      AiB = AiB + x                       SOLVED - greater_than

categories = {}                             # Dict from category to elements in that category
sets = {}                                   # Dict from (cat_a, element_a, cat_b) to subset of cat_b linked to element_a

# Code for solving a logic puzzle

def generate_sets(all_sets, all_categories):
    for key_a in all_categories:
        for key_b in all_categories:
            for element in all_categories[key_a]:
                if not key_a is key_b:
                    all_sets[ (key_a, element, key_b) ] = set( all_categories[key_b] )

def complement(A_set, universal):
    return universal-A_set

def is_element(A_set, element):
    return A_set & set([element])

def exclude_element(A_set, element):
    if element in A_set:
        A_set.remove(element)
    return A_set
    #return ( complement(A_set & set([element]), A_set) )

##### CLUE FUNCTIONS ##########################################################

# Type 1 clue solution
def set_element(el_A, el_B, all_sets, all_categories, inner_call=False):
    category_A = get_parent_set_category(el_A, all_categories)
    category_B = get_parent_set_category(el_B, all_categories)
    all_els_A = get_full_parent_set(el_A, all_categories)           # get all elements of parent set of el_A
    
    set_A = all_sets[ (category_A, el_A, category_B) ]
    set_A = is_element(set_A, el_B)
    all_sets[ (category_A, el_A, category_B) ] = set_A
    
    for el in all_els_A:
        if el != el_A:
            temp_set = all_sets[ (category_A, el, category_B) ]
            temp_set = exclude_element(temp_set, el_B)
            all_sets[ (category_A, el, category_B) ] = temp_set
    
    # Because sets are symmetric, if el_A on cat_B is el_B, then el_B on cat_A is el_A
    if not inner_call:
        set_element(el_B, el_A, all_sets, all_categories, inner_call=True)
    
    return True

# Type 2 clue solution
def set_not_element(el_A, el_B, all_sets, all_categories):
    category_A = get_parent_set_category(el_A, all_categories)
    category_B = get_parent_set_category(el_B, all_categories)
    set_A = all_sets[ (category_A, el_A, category_B) ]
    set_A = exclude_element(set_A, el_B)
    all_sets[ (category_A, el_A, category_B) ] = set_A

    return True

# Type 3 clue solution
# For clue that says el_A is either el_B or el_C where el_A, el_B, and el_C are
# members of sets A, B, and C respectively
def is_one_of(el_A, el_B, el_C, all_sets, all_categories):
    category_A = get_parent_set_category(el_A, all_categories)
    category_B = get_parent_set_category(el_B, all_categories)
    category_C = get_parent_set_category(el_C, all_categories)
    set_AB = all_sets[ (category_A, el_A, category_B) ]
    set_AC = all_sets[ (category_A, el_A, category_C) ]
    set_BC = all_sets[ (category_B, el_B, category_C) ]
    set_CB = all_sets[ (category_C, el_C, category_B) ]
    
    set_BC = exclude_element(set_BC, el_C)
    all_sets[ (category_B, el_B, category_C) ] = set_BC
    set_CB = exclude_element(set_CB, el_B)
    all_sets[ (category_C, el_C, category_B) ] = set_CB
    if len( set_AB & set( [el_B] ) ) == 0:
        #set_AC = set_AC & set( [el_C] )
        #all_sets[ (category_A, el_A, category_C) ] = set_AC
        return set_element(el_A, el_C, all_sets, all_categories)
        #return True
    elif len( set_AC & set( [el_C] ) ) == 0:
        #set_AB = set_AB & set( [el_B] )
        #all_sets[ (category_A, el_A, category_B) ] = set_AB
        return set_element(el_A, el_B, all_sets, all_categories)
        #return True
    return False

# Type 4 clue solution
def multi_is_one_of(elements_A, elements_B, all_sets, all_categories):
    # Exclude all elements in elements_A from the other elements in elements_A, same for B
    mutual_exclude(elements_A, all_sets, all_categories)
    mutual_exclude(elements_B, all_sets, all_categories)
    check_single_mapping(elements_A, elements_B, all_sets, all_categories)
    pairings = pair_categories(elements_A, elements_B, all_sets, all_categories)
    return remove_pairs(elements_A, elements_B, pairings, all_sets, all_categories)

# Exclude elements in a list from the sets of the other elements in that list
def mutual_exclude(elements, all_sets, all_categories):
    for el_A in elements:
        category_A = get_parent_set_category(el_A, all_categories)
        for el_B in elements:
            category_B = get_parent_set_category(el_B, all_categories)
            if category_A != category_B:
                set_A = all_sets[ (category_A, el_A, category_B) ]
                set_A = exclude_element(set_A, el_B)
                all_sets[ (category_A, el_A, category_B) ] = set_A

# Check to see if everything in elements_B belongs to the same set, if so, set
# the sets of elements_A on category_B to only the elements in elements_B
def check_single_mapping(elements_A, elements_B, all_sets, all_categories):
    cats_B = set( [ get_parent_set_category(el, all_categories) for el in elements_B ] )
    if len(cats_B) == 1:
        cat_B = cats_B.pop()
        for el_A in elements_A:
            cat_A = get_parent_set_category(el_A, all_categories)
            set_A = all_sets[ (cat_A, el_A, cat_B) ]
            set_A = set_A & set(elements_B)
            all_sets[ (cat_A, el_A, cat_B) ] = set_A

# TODO : Fix bug in pair_categories
# Pair any elements in elements_A to those in elements_B when there is enough information
def pair_categories(elements_A, elements_B, all_sets, all_categories):
    categories_B = list( set( [ get_parent_set_category(el, all_categories) for el in elements_B ] ) )
    pairings = []
    for el_A in elements_A:
        category_A = get_parent_set_category(el_A, all_categories)
        for cat in categories_B:
            if cat != category_A:
                #universal = all_sets[ (category_A, el_A, cat) ]    # TODO make sure this is the right universal set
                universal = set( [ i for i in elements_B if i in all_categories[cat] ] )
                seed_set = set()
                # yes, elements_A, not B, look at others in the same list
                for el_B in elements_A:
                    if el_A != el_B:
                        category_B = get_parent_set_category(el_B, all_categories)
                        if category_B != cat:
                            seed_set = seed_set | all_sets[ (category_B, el_B, cat) ]
                
                seed_set = complement(seed_set, universal)
                set_A = all_sets[ (category_A, el_A, cat) ]
                res = set_A & seed_set
                
                # If the resulting set is empty, there aren't enough constraints to specify
                if len(res) != 0:
                    all_sets[ (category_A, el_A, cat) ] = res       # Should this be inside the len == 1?
                    if len(res) == 1:
                        pairings.append( (el_A, res.pop()) )
    return pairings

# If there are pairs, remove them from elements_A and elements_B (we don't need to solve them again)
# If elements_A and elements_B are emptied, the clue is fully solved
def remove_pairs(elements_A, elements_B, pairings, all_sets, all_categories):
    for pair in pairings:
        elements_A.remove( pair[0] )
        elements_B.remove( pair[1] )
    if len(elements_A) == 0 and len(elements_B) == 0:
        return True
    elif len(elements_A) == 1 and len(elements_B) == 1:
        el_A = elements_A.pop()
        el_B = elements_B.pop()
        cat_A = get_parent_set_category(el_A, all_categories)
        cat_B = get_parent_set_category(el_B, all_categories)
        set_A = all_sets[ (cat_A, el_A, cat_B) ]
        set_A = is_element(set_A, el_B)
        all_sets[ (cat_A, el_A, cat_B) ] = set_A
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
def greater_than(el_A, el_B, category, all_sets, all_categories, value=None):
    # el_A and el_B in separate categories => exclude a and b from each other
    category_A = get_parent_set_category(el_A, all_categories)
    category_B = get_parent_set_category(el_B, all_categories)
    set_A = all_sets[ (category_A, el_A, category) ]
    set_B = all_sets[ (category_B, el_B, category) ]
    
    # If el_A on category is greater than el_B on category and they are not in the same category
    # then el_A on B does not include el_B and el_B on A does not include el_A
    if category_A != category_B:
        set_AB = all_sets[ (category_A, el_A, category_B) ]
        set_BA = all_sets[ (category_B, el_B, category_A) ]
        set_AB = exclude_element(set_AB, el_B)
        set_BA = exclude_element(set_BA, el_A)
        all_sets[ (category_A, el_A, category_B) ] = set_AB
        all_sets[ (category_B, el_B, category_A) ] = set_BA
        
    if value is None:
        set_A = set( [ s for s in set_A if s > min(set_B) ] )
        set_B = set( [ s for s in set_B if s < max(set_A) ] )
    else:
        set_A = set_A & set( [ s+value for s in set_B ] )
        set_B = set_B & set( [ s-value for s in set_A ] )
    
    all_sets[ (category_A, el_A, category) ] = set_A
    all_sets[ (category_B, el_B, category) ] = set_B
    
    if len(set_A) == 1 or len(set_B) == 1:
        return True     # This clue can give no more information
    return False        # There is still information to be gained

##### END CLUE FUNCTIONS ######################################################

# Given an element and all the sets, return the set that contains the element
def get_parent_set(element, all_sets):
    for A in all_sets:
        if element in A:
            return A

def get_full_parent_set(element, all_categories):
    for key in all_categories:
        if element in all_categories[key]:
            return all_categories[key]

def get_parent_set_category(element, all_categories):
    for key in all_categories:
        if element in all_categories[key]:
            return key

# Unpacks key into caT_A, el_A, cat_B
def unpack_key(key):
    return key[0], key[1], key[2]

##### SOLUTION FUNCTIONS ######################################################
# Functions for solving
# 1) symmetrize - apply the symmetry relation so if A => B, B => A
# 2) exclude_solved - exclude solutions of one set from other sets of the same category
# 3) solve_all_singleton - solves when an element can only be the solution of one set
# 4) chain_sets - applies transitivity so if A => B, then (A on C) and (B on C) are the intersection of the two
# 5) n_of_n - if n sets share the same n elements, exclude these n elements from sets of the same category
# 6) remove_chain_exclusion - if a set (cat_A, el_A, cat_B) is solved to be el_B, remove el_B
#       from all (cat_C, el_C, cat_B) for which (cat_A, el_A, cat_C) does NOT contain el_C

# TODO : Implement more complex searches:

# If a set (cat_A, el_A, cat_B) is solved to be el_B, remove el_B
# from all (cat_C, el_C, cat_B) for which (cat_A, el_A, cat_C) does NOT contain el_C
def remove_chain_exclusion(all_sets, all_categories):
    for key in all_sets:
        if len( all_sets[key] ) == 1:
            cat_A, el_A, cat_B = unpack_key(key)
            el_B = all_sets[key].pop()
            all_sets[key].add(el_B)
            
            for cat_C in all_categories.keys():
                if cat_A != cat_C and cat_B != cat_C:
                    set_AC = all_sets[ (cat_A, el_A, cat_C) ]
                    set_C = set( all_categories[cat_C] )
                    excluded = complement(set_AC, set_C)
                    for el_C in excluded:
                        set_not_element(el_C, el_B, all_sets, all_categories)
                        

# Because the sets are symmetric, for any set element_A on category_B with only one element_B,
# elemet_A should be the only element of the set element_B on category_A
def symmetrize(all_sets):
    for key in all_sets:
        if len( all_sets[ key ] ) == 1:
            cat_A = key[0]
            el_A = key[1]
            cat_B = key[2]
            el_B = None
            for el in all_sets[key]:
                el_B = el
            
            all_sets[ (cat_B, el_B, cat_A) ] = set( [el_A] )

# If a set is solved ( el_A on cat_B contains one element, el_B ), exclude el_B from other sets from cat_A
def exclude_solved(all_sets, all_categories):
    for key in all_sets:
        # for the sets that have been solved
        if len( all_sets[key] ) == 1:
            cat_A = key[0]
            el_A = key[1]
            cat_B = key[2]
            el_B = None
            for el in all_sets[key]:
                el_B = el
            
            # for all other members of cat_A, exclude el_B from their sets on cat_B
            for el in all_categories[cat_A]:
                if el != el_A:
                    temp_set = all_sets[ (cat_A, el, cat_B) ]
                    temp_set = exclude_element(temp_set, el_B)
                    all_sets[ (cat_A, el, cat_B) ] = temp_set

# If one element of category_B can be found in the set for element_A from category_A but
# no other sets from category_A, then that element is the solution for element_A on category_B
def solve_all_singleton(all_sets, all_categories):
    cats = list( all_categories.keys() )
    for cat_A in cats:
        els = all_categories[cat_A]
        for el_A in els:
            for cat_B in cats:
                if cat_A != cat_B:
                    solve_singleton(cat_A, el_A, cat_B, els, all_sets, all_categories)

# Finds the union of all sets from all elements of cat_A on cat_B, excluing the set for el_A
# then finds the set of elements included in el_A on cat_B that are not present in the set
# of the other elements from cat_A
def solve_singleton(cat_A, el_A, cat_B, els, all_sets, all_categories):
    set_A = all_sets[ (cat_A, el_A, cat_B) ]
    other_set = set()
    for el_B in els:
        if el_A != el_B:
            other_set = other_set | all_sets[ (cat_A, el_B, cat_B) ] 
    
    # see if there is anyhting left in the complement of their intersection
    remaining = complement(set_A & other_set, set_A)
    # this intersection can be an empty set or a set of one element
    if len(remaining) == 1:
        solution_el = None
        for item in remaining:
            solution_el = item
        set_element(el_A, solution_el, all_sets, all_categories)
    
# if we know that (cat_A, el_A, cat_B) is el_B, then we know that 
# (cat_A, el_A, cat_C) and (cat_B, el_B, cat_C) will both equal their intersection
#def chain_sets(all_sets, all_categories):
#    cats = list( all_categories.keys() )
#    for key in all_sets:
#        # Find the sets that have been solved
#        if len( all_sets[key] ) == 1:
#            # Gather the information nneded to associate el_A and el_B
#            cat_A = key[0]
#            el_A = key[1]
#            cat_B = key[2]
#            el_B =all_sets[key].pop()
#            all_sets[key].add(el_B)
#            
#            for cat_C in cats:
#                # Only operate on sets other than A and B
#                if cat_A != cat_C and cat_B != cat_C:
#                    # Set el_A on cat_C and el_B on cat_C to be their intersection
#                    set_AC = all_sets[ (cat_A, el_A, cat_C) ]
#                    set_BC = all_sets[ (cat_B, el_B, cat_C) ]
#                    result = set_AC & set_BC
#                    all_sets[ (cat_A, el_A, cat_C) ] = set(result)
#                    all_sets[ (cat_B, el_B, cat_C) ] = set(result)

# If (cat_A, el_A, cat_B) = {el_B1, el_B2}, then (cat_A, el_A, cat_C) = (cat_A, el_A, cat_C) & ( (cat_B, el_B1, cat_C) | (cat_B, el_B2, cat_C) )
def chain_sets(all_sets, all_categories):
    cats = list( all_categories.keys() )
    for key in all_sets:
        cat_A, el_A, cat_B = unpack_key(key)
        els_B = all_sets[key]
        
        for cat_C in cats:
            set_BC = set()
            if cat_A != cat_C and cat_B != cat_C:
                for el_B in els_B:
                    set_BC = set_BC | all_sets[ (cat_B, el_B, cat_C) ]
                
                set_AC = all_sets[ (cat_A, el_A, cat_C) ]
                set_AC = set_AC & set_BC
                all_sets[ (cat_A, el_A, cat_C) ] = set_AC
    
# if n sets from a category have the same n elements, then the remaining sets cannot have those
# n elements
def n_of_n(all_sets, all_categories):
    cats = list( all_categories.keys() )
    for cat_A in cats:
        for cat_B in cats:
            if cat_A != cat_B:
                for el_AA in all_categories[cat_A]:
                    set_A = all_sets[ (cat_A, el_AA, cat_B) ]
                    same = [el_AA]
                    for el_AB in all_categories[cat_A]:
                        if el_AA != el_AB and all_sets[ (cat_A, el_AB, cat_B) ] == set_A:
                            same.append(el_AB)
                    
                    # n sets of n elements but not just all of the possibilities
                    if len(same) != len(all_categories) and len(same) == len(set_A):
                        exclude_n_of_n(same, set_A, cat_A, cat_B, all_sets, all_categories)

def exclude_n_of_n(same_sets, elements, cat_A, cat_B, all_sets, all_categories):
    for el_A in all_categories[cat_A]:
        if not el_A in same_sets:
            for el_B in elements:
                set_not_element(el_A, el_B, all_sets, all_categories)

##### END SOLUTION FUNCTIONS ##################################################

# Get the cominded lengths of all of the sets
def get_total_length(all_sets):
    size = 0
    for key in all_sets:
        size += len( all_sets[key] )
    return size

# Puzzle will be solved when all sets have length 1
def is_solved(all_sets):
    largest = 0
    for key in all_sets:
        largest = max( largest, len( all_sets[key] ) )
    return largest == 1

# solved a puzzle given the sets, categories, and clues for the puzzle
# clues are stored as a 2-tuple of (function, arguments)
def solve_puzzle(clues, all_sets, all_categories):
    solutions = {}
    solved = [False for i in range(len(clues))]
    
    # Iterate until no new changes have been made
    change = 1
    while change:
        print("New Loop")
        before = get_total_length(all_sets)
        print(before)
        
        solve_clues(clues, solved, all_sets, all_categories)
        print(get_total_length(all_sets))
        #show_sets(all_sets)
        
        chain_sets(all_sets, all_categories)
        print(get_total_length(all_sets))
        #show_sets(all_sets)
        exclude_solved(all_sets, all_categories)
        print(get_total_length(all_sets))
        solve_all_singleton(all_sets, all_categories)
        print(get_total_length(all_sets))
        #show_sets(all_sets)
        n_of_n(all_sets, all_categories)
        print(get_total_length(all_sets))
        remove_chain_exclusion(all_sets, all_categories)
        print(get_total_length(all_sets))
        symmetrize(all_sets)
        print(get_total_length(all_sets))
        
        after = get_total_length(all_sets)
        print(after)
        change = before - after
    
    if is_solved(all_sets):
        cats = list( all_categories.keys() )
        primary_cat = cats[0]
        for el in all_categories[cats[0]]:
            solutions[el] = []
        
        for cat in cats[1:]:
            for key in solutions:
                solutions[key].append( all_sets[ (primary_cat, key, cat) ] )
    
    return solutions

# Iterates through the clues, solving until no changes are made or until everything has been solved
def solve_clues(clues, solved, all_sets, all_categories):
    # Iterate through the clues until no changes have been made
    changed = not all(solved)              # True until all clues are solved
    while changed:
        total_before = get_total_length(all_sets)
        
        for i in range(len(clues)):
            if not solved[i]:
                func = clues[i][0]
                args = clues[i][1]
                solved[i] = func( *args )
                        
        total_after = get_total_length(all_sets)
        changed = not( total_before == total_after )            # same length means nothing has changed

def test(all_sets, all_categories):
    all_categories = {"Attendees":["Jack", "Kit", "Mitch", "Ned", "Pam"],
                  "Gifts":["Blender", "Blu-ray", "Juicer", "Planter", "Toaster"],
                  "Prices":[400, 425, 450, 475, 500]}
    generate_sets(all_sets, all_categories)
    
    clues = []
    clues.append( ( set_element, ["Pam", "Juicer", all_sets, all_categories] ) )
    clues.append( ( set_element, [500, "Blu-ray", all_sets, all_categories] ) )
    clues.append( ( multi_is_one_of, [["Mitch", "Juicer"], [475, 450], all_sets, all_categories] ) )
    clues.append( ( is_one_of, ["Kit", "Juicer", 400, all_sets, all_categories] ) )
    clues.append( ( is_one_of, ["Ned", 475, "Blender", all_sets, all_categories] ) )
    clues.append( ( set_not_element, [475, "Planter", all_sets, all_categories] ) )
    clues.append( ( greater_than, ["Mitch", "Blender", "Prices", all_sets, all_categories, 50] ) )
    
    #return clues
    return solve_puzzle(clues, all_sets, all_categories)

def show_sets(all_sets):
    for key in all_sets:
        print(key, " -> ", all_sets[key])

def solve_n_clues(clues, sets, categories, n):
    func = clues[n%len(clues)][0]
    args = clues[n%len(clues)][1]
    func( *args )