#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import collections
import itertools
import random

def consoleLabel(deduper): # pragma : no cover
    '''
    Command line interface for presenting and labeling training pairs
    by the user
    
    Argument :
    A deduper object
    '''

    finished = False

    while not finished :
        uncertain_pairs = deduper.getUncertainPair()

        labels = {'distinct' : [], 'match' : []}

        for record_pair in uncertain_pairs:
            label = ''
            labeled = False

            for pair in record_pair:
                for field in deduper.data_model.comparison_fields:
                    line = "%s : %s\n" % (field, pair[field])
                    sys.stderr.write(line)
                sys.stderr.write('\n')

            sys.stderr.write('Do these records refer to the same thing?\n')

            valid_response = False
            while not valid_response:
                sys.stderr.write('(y)es / (n)o / (u)nsure / (f)inished\n')
                label = sys.stdin.readline().strip()
                if label in ['y', 'n', 'u', 'f']:
                    valid_response = True

            if label == 'y' :
                labels['match'].append(record_pair)
                labeled = True
            elif label == 'n' :
                labels['distinct'].append(record_pair)
                labeled = True
            elif label == 'f':
                sys.stderr.write('Finished labeling\n')
                finished = True
            elif label != 'u':
                sys.stderr.write('Nonvalid response\n')
                raise

        if labeled :
            deduper.markPairs(labels)
        

def trainingDataLink(data_1, data_2, common_key, training_size=50000) :
    '''
    Construct training data for consumption by the ActiveLearning 
    markPairs method from already linked datasets.
    
    Arguments : 
    data_1        -- Dictionary of records from first dataset, where the keys
                     are record_ids and the values are dictionaries with the 
                     keys being field names

    data_2        -- Dictionary of records from second dataset, same form as 
                     data_1
    
    common_key    -- The name of the record field that uniquely identifies 
                     a match
    
    training_size -- the rough limit of the number of training examples, 
                     defaults to 50000
    
    Warning:
    
    Every match must be identified by the sharing of a common key. 
    This function assumes that if two records do not share a common key 
    then they are distinct records. 
    '''
    
    
    identified_records = collections.defaultdict(lambda: [[],[]])
    matched_pairs = set()
    distinct_pairs = set()

    for record_id, record in data_1.items() :
        identified_records[record[common_key]][0].append(record_id)

    for record_id, record in data_2.items() :
        identified_records[record[common_key]][1].append(record_id)

    for keys_1, keys_2 in identified_records.values() :
        if keys_1 and keys_2 :
            matched_pairs.update(itertools.product(keys_1, keys_2))

    distinct_pairs = set(itertools.product(data_1.keys(), data_2.keys()))
    distinct_pairs -= matched_pairs
    distinct_pairs = random.sample(distinct_pairs, training_size)

    matched_records = [(data_1[key_1], data_2[key_2])
                       for key_1, key_2 in matched_pairs]

    distinct_records = [(data_1[key_1], data_2[key_2])
                        for key_1, key_2 in distinct_pairs]

    training_pairs = {'match' : matched_records, 
                      'distinct' : distinct_records} 

    return training_pairs        
        

def trainingDataDedupe(data, common_key, training_size=50000) :
    '''
    Construct training data for consumption by the ActiveLearning 
    markPairs method from an already deduplicated dataset.
    
    Arguments : 
    data          -- Dictionary of records, where the keys are record_ids and 
                     the values are dictionaries with the keys being 
                     field names

    common_key    -- The name of the record field that uniquely identifies 
                     a match
    
    training_size -- the rough limit of the number of training examples, 
                     defaults to 50000
    
    Warning:
    
    Every match must be identified by the sharing of a common key. 
    This function assumes that if two records do not share a common key 
    then they are distinct records. 
    '''

    
    identified_records = collections.defaultdict(list)
    matched_pairs = set()
    distinct_pairs = set()

    for record_id, record in data.items() :
        identified_records[record[common_key]].append(record_id)

    for record_ids in identified_records.values() :
        if len(record_ids) > 1 :
            matched_pairs.update(itertools.combinations(sorted(record_ids), 2))

    distinct_pairs.update(itertools.combinations(sorted(data.keys()), 2))
    distinct_pairs -= matched_pairs

    distinct_pairs = random.sample(distinct_pairs, training_size)

    matched_records = [(data[key_1], data[key_2])
                       for key_1, key_2 in matched_pairs]

    distinct_records = [(data[key_1], data[key_2])
                        for key_1, key_2 in distinct_pairs]

    training_pairs = {'match' : matched_records, 
                      'distinct' : distinct_records} 

    return training_pairs
