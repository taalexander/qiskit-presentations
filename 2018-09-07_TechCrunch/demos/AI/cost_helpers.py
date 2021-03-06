# -*- coding: utf-8 -*-

# Copyright 2018, IBM.
#
# This source code is licensed under the Apache License, Version 2.0 found in
# the LICENSE.txt file in the root directory of this source tree.

import numpy as np
from collections import Counter

def entangler_map_creator(n):
    if n == 2:
        entangler_map = {0: [1]}
    elif n ==3:
        entangler_map = {0: [2, 1],
                 1: [2]}
    elif n == 4:
        entangler_map = {0: [2, 1],
                 1: [2],
                 3: [2]}
    elif n == 5:
        entangler_map = {0: [2, 1],
                 1: [2],
                 3: [2, 4],
                 4: [2]}
    return entangler_map

def assign_label(key,class_labels):

    if len(class_labels) == 2 and int(len(list(key))%2) != 0:
        vote_count = Counter(key)
        top_count = vote_count.most_common(2)
        result = int(top_count[0][0])
        return class_labels[result]

    elif len(class_labels) == 2:
        hamming_weight = sum([int(k) for k in list(key)]) 
        is_odd_parity = hamming_weight & 1

        if is_odd_parity:
            return class_labels[1]
        else:
            return class_labels[0]

    elif len(class_labels) == 3:
        first_half = int(np.floor(len(list(key))/2))
        modulo = int(len(list(key))%2)
        hamming_weight_1 = sum([int(k) for k in list(key)[0:first_half+modulo]]) #First half of key
        hamming_weight_2 = sum([int(k) for k in list(key)[first_half+modulo:]]) #Second half of key
        is_odd_parity_1 = hamming_weight_1 & 1
        is_odd_parity_2 = hamming_weight_2 & 1
        
        if (not is_odd_parity_1) & (not is_odd_parity_2): #Both halves even
            return class_labels[0]
        elif is_odd_parity_1 & is_odd_parity_2: #Both halves odd
            return class_labels[2]
        else: #One half even, one half odd
            return class_labels[1]
    else:
        total_size = 2**len(list(key))
        class_step = np.floor(total_size/len(class_labels))
        key_order = int(np.floor(int(key, 2)/class_step))
        if key_order < len(class_labels):
            return class_labels[key_order]
        else:
            return class_labels[-1]
        
def cost_estimate_sigmoid(shots, probs, expected_category):

    p = probs.get(expected_category)
 
    if p < 0:
        p=0

    elif p > 1:
        p=1
    
    probs_without_measured_expectation = [v for key, v in probs.items() if key != expected_category] 

    number_of_classes = len(probs)

    if number_of_classes == 2:
        if np.isclose(p, 0.0): 
            sig = 1
        elif np.isclose(p, 1.0):
            sig = 0
        else:
            denominator = np.sqrt(2*p*(1-p))
            x = np.sqrt(shots)*(0.5-p)/denominator
            sig = 1/(1+np.exp(-x))
    elif number_of_classes == 3:
        if np.isclose(p, 0.0): 
            sig = 1
        elif np.isclose(p, 1.0):
            sig = 0
        else:
            denominator = np.sqrt(2*p*(1-p))
            numerator = np.sqrt(shots)*((1+abs(probs_without_measured_expectation[0]-probs_without_measured_expectation[1]))/3-p)
            x = numerator/denominator
            sig = 1/(1+np.exp(-x))
    return sig

def return_probabilities(counts, class_labels):
    hits =  sum(counts.values())

    result = {class_labels[p]:0 for p in range(len(class_labels))}
    for (key, item) in counts.items():
        hw = assign_label(key,class_labels)  
        result[hw] += counts[key]/hits

    return result


