'''
-------------------------------------
Porject name: MS-PS implementation
Course: CS-583 18'Fall

Group member: Ting Han, Bohan Fan
Compiler version: python 3.7
-------------------------------------
'''



import os
import re
import itertools
from collections import Counter
import math

def contains(big, small):
	# just add one more line so this function can also be folded
	return len(set(big).intersection(set(small))) == len(small)

def is_sequence_sdc_satisfied(sequence):
	# print('sequence is sdc satisfied',sequence)
	# print('len of sequence', len(sequence))
	if not sequence:
		return False
	if len(sequence) > 1:
		for item1 in sequence:
			sup_item1 = actual_supports.get(item1)
			for item2 in sequence:
				if not item1 == '_' and not item2 == '_' and not item1 == item2:
					if abs(sup_item1 - actual_supports.get(item2)) > sdc:
						return False
	return True

def write_output(output_list):
	output_list = sorted(output_list, key = pattern_length) # sort the output based on pattern length
	output_text = '' # initialize empty string to append the output text

	cur_length = 1 # initialize current length as 1

	while True: # iterate until there are no patterns of specified length
		# get all the patterns of current length from output
		cur_length_patterns = list(filter (lambda a: pattern_length(a) == cur_length, output_list))
		if not cur_length_patterns: # break from the loop if the list is empty
			break

		# print the currnt length and number of patterns for current length 
		output_text += 'The number of length ' + str(cur_length) + ' sequential pattern is:' + str(len(cur_length_patterns)) + '\n'
		
		# print all the patterns with their support counts
		for (pattern, sup_count) in cur_length_patterns:
			str_pattern = '<{' + '}{'.join([','.join(itemset) for itemset in pattern]) + '}>'
			output_text += 'Pattern:' + str_pattern + ' Count:' + str(sup_count) + '\n'

		cur_length += 1 # increment the current length
		output_text += '\n'


	print(output_text)
	output_file = open(out_file, 'w')
	output_file.write(output_text)
	output_file.close()

def pattern_length(output_tuple):
	seq_pattern = output_tuple[0] # get the sequential pattern

	while isinstance(seq_pattern[0], list): # chain it until all sub_lists are removed
		seq_pattern = list(itertools.chain(*seq_pattern))

	return len(seq_pattern) # return the length of the pattern

def remove_item(source_list, item_to_del):
	filtered_list = [] # declare list to contain filter results

	# check to see if list has sub lists as items
	if source_list and isinstance(source_list[0], list):
		for child_list in source_list:
			filtered_child_list = remove_item(child_list, item_to_del)
			if filtered_child_list:
				filtered_list.append(filtered_child_list)
	else:
		filtered_list = list(filter(lambda a: a != item_to_del, source_list))

	return filtered_list # return the filtered list from current recursion

def contains_in_order(sq_itemset, pr_itemset):
	if(contains(sq_itemset, pr_itemset)):
		cur_pr_item = 0
		cur_sq_item = 0

		while cur_pr_item < len(pr_itemset) and cur_sq_item < len(sq_itemset):
			if pr_itemset[cur_pr_item] == sq_itemset[cur_sq_item]:
				cur_pr_item += 1
				if cur_pr_item == len(pr_itemset):
					return True
			cur_sq_item += 1
	return False

def support_count(sequences, req_item):
	flattened_sequences = [ list(set((itertools.chain(*sequence)))) for sequence in sequences ]
	support_counts = dict(Counter(item for flattened_sequence in flattened_sequences for item in flattened_sequence))
	return support_counts.get(req_item)

def has_item(source_list, item):
	# print('source_list', source_list)
	if source_list:
		# print(source_list[0])
		while isinstance(source_list[0], list):
			# print(source_list[0])
			source_list = list(itertools.chain(*source_list))
			# print(source_list)
		return item in source_list
	return False

def sdc_filter_on_item(source_list, base_item, base_item_support, supports, sd_constraint):
  filtered_list = []    # Declare list to contain filter results
  # print(source_list)
  # Check to see if list has sub lists as items    
  if source_list and isinstance(source_list[0], list):
  	for child_list in source_list:
  		# print(child_list)
  		filtered_child_list = sdc_filter_on_item(child_list, base_item, base_item_support, supports, sd_constraint)    # Recurse for filtering each child_list
  		# print(filtered_child_list)
  		if filtered_child_list:   # Append only the non-empty lists
  			filtered_list.append(filtered_child_list)  
    
  else:   # Remove items that do not satisfy support difference constraint
    for item in source_list:
    	# print(item)
    	# print("Item:",item,"Support:",item_supports.get(item),"Diff:",abs(item_supports.get(item) - base_item_support))
    	if not item == base_item and abs(supports.get(item) - base_item_support) > sd_constraint:  # Item doesn't satisfy SDC
    		continue
    	else:   # Item satisfies SDC
        	filtered_list.append(item)

  return filtered_list    # Return the filtered list from current recursion

def prefix_span(prefix, item_sequences, base_item, mis_count):
	print('Prefix:', prefix)

	#compute the projected databese for the current prefix
	projected_db = compute_projected_database(prefix, item_sequences, base_item, mis_count)
	print('DB:')
	print('\n'.join([str(sequence) for sequence in projected_db]))

	# find the prefix_length + 1 sequential patterns

	if projected_db: # check if the projected database has any sequences
		# initialize local variabls
		prefix_last_itemset = prefix[-1] #last itemset in prefix
		all_template_1_items = [] # to hold all items for template 1 match i.e. {30, x} or {_, x}
		all_template_2_items = [] # to hold all items for template 2 match i.e. {30}{x}

		for proj_sequence in projected_db:
			itemset_index = 0
			template_1_items = [] # to hold items for template 1 match from current sequence
			template_2_items = [] # to hold items for template 2 match from current sequence

			while itemset_index < len(proj_sequence): # iterate through itemsets in sequence
 				cur_itemset = proj_sequence[itemset_index] # current itemset in sequence

 				if has_item(cur_itemset, '_'): # Add items following '_' to template 1 list if it's a {_, x} match
 					template_1_items += cur_itemset[1:]

 					# itemset doesn't contain '_', check for other matches
 				else:
 					if contains_in_order(cur_itemset, prefix_last_itemset):# check if current itemset contains last itemset of prerix i.e. {30, x} match
 						template_1_items += cur_itemset[cur_itemset.index(prefix_last_itemset[-1])+1:]

 					template_2_items += cur_itemset
 				itemset_index += 1
			# add only the unique elements from both lists of current sequence to maintain lists as each elemenet is only considered once for a sequence
			all_template_1_items += list(set(template_1_items))
			all_template_2_items += list(set(template_2_items))
			# print('template 1 items:', all_template_1_items)
			# print('template 2 items:', all_template_2_items)
 		# compute the total occurrences of each element for each template i.e. numer of sequences it satisfied for a template match
		dict_template_1 = dict(Counter(item for item in all_template_1_items))
		dict_template_2 = dict(Counter(item for item in all_template_2_items))

		# print('template 1 items support:', dict_template_1)
		# print('template 2 items support:', dict_template_2)
		# print('dict_template_1.items()', dict_template_1.items())

		freq_sequential_patterns = [] # initialize empty list to contain obtained sequential patterns

 		# for both the templat matches, generate frequent sequential patterns i.e. patterns which have support count >= MIS count
		for item, sup_count in dict_template_1.items():
			# print((item,sup_count))
			if sup_count >= mis_count:
 				freq_sequential_patterns.append((prefix[:-1] + [prefix[-1] + [item]], sup_count))
 				# print('freq_sequential_patterns', freq_sequential_patterns)
		
		for item, sup_count in dict_template_2.items():
 			if sup_count >= mis_count:
 				# append the item contained in  a new itemset to the prefix
 				freq_sequential_patterns.append((prefix + [[item]], sup_count)) # add the pattern with its support count to frequent pattern list
 		# print('sequential patterns before SDC:', [])
		freq_sequential_patterns = [(pattern, sup_count) for pattern, sup_count in freq_sequential_patterns if is_sequence_sdc_satisfied(list(set(itertools.chain(*pattern))))]
	 	# print('sequential patterns before SDC:', [])
		for (seq_pattern, sup_count) in freq_sequential_patterns: # iterate through pattersn obtained
			if has_item(seq_pattern, base_item): # add the pattern to output list if it contains base item
				output_patterns.append((seq_pattern, sup_count))
			prefix_span(seq_pattern, item_sequences, base_item, mis_count) # call prefex recursively with the pattern as prefix

def compute_projected_database(prefix, item_sequences, base_item, mis_count):
	projected_db = []

	# populate the projected database with projected sequences
	for sequence in item_sequences:
		cur_pr_itemset = 0
		cur_sq_itemset = 0
		# print('len', len(sequence))

		while cur_pr_itemset < len(prefix) and cur_sq_itemset < len(sequence):
			if contains_in_order(sequence[cur_sq_itemset], prefix[cur_pr_itemset]): # sequence itemset contains the prefix itemset, move to next prefix itemset
				cur_pr_itemset += 1
				if cur_pr_itemset == len(prefix): break # all prefix itemsets are present in the sequence

			cur_sq_itemset += 1 # move to next sequence itemset 

		if cur_pr_itemset == len(prefix): # prefix was present in the current sequence
			# print('prefix[-1][-1]', prefix[-1])
			projected_sequence = project_sequence(prefix[-1][-1], sequence[cur_sq_itemset:]) # get the projected sequence
			if projected_sequence: # non-empty sequence, add to projected database
				projected_db.append(projected_sequence)

	# print('DB1:')
	# print('\n'.join([str(sequence) for sequence in projected_db]))

	# check if any frequent items are left
	validation_db = remove_empty_elements([[[item for item in itemset if not item == '_'] for itemset in sequence] for sequence in projected_db])
	if validation_db: # non-empty database
		return remove_empty_elements(projected_db) # remove empty elements and return the projected database
	else: # empty database
		return validation_db

def project_sequence(prefix_last_itemset, suffix):
	# print('suffix', suffix)
	suffix_first_itemset = suffix[0]

	if prefix_last_itemset == suffix_first_itemset[-1]: # template 2 projection, return suffix - current_itemset
		return suffix[1:]
	else: # template 1 projection, remove items from first itemset of suffix that are before the index of prefix's last item and put '_' as first element
		suffix[0] = ['_'] + suffix_first_itemset[suffix_first_itemset.index(prefix_last_itemset)+1:]
		return suffix

def remove_empty_elements(source_list):
	filtered_list = [] # declare list to contain filter results

	# check to see if list has sub lists as items
	if source_list and isinstance(source_list[0], list):
		for child_list in source_list:
			filtered_child_list = remove_empty_elements(child_list) # recurse for filtering each child_list

			if filtered_child_list: # append only non-empty lists
				filtered_list.append(filtered_child_list)

	else: 
		filtered_list = source_list

	return filtered_list 

def remove_infrequent_items(item_sequences, min_support_count):
	# get the support count for each intem in supplied sequence databse
	flattened_sequences = [ list(set(itertools.chain(*sequence))) for sequence in item_sequences]
	support_counts = dict(Counter(item for flattened_sequence in flattened_sequences for item in flattened_sequence))
	# for python 3 and above version, you may need to add one line as follow to make sure that
	# support_counts does not contain any empty key, but for python 2.7, you don't need to use this line
	support_counts = {key: value for key, value in support_counts.items() if key is not ''} # line for python 3.x, not for python 2.7
	# comments for above lines: in the project, if the dataset contains empty line within data, for python 3.x, it will count it as '', which 
	# means that it will generate dictionary: {'': 1}, but for python 2.7, we don't have to consider this problem.
	# the method to modify in python 3 is to add the above line to remove this dict.
	# remove the infrequent items from the sequence database
	filtered_item_sequences = [[[item for item in itemset if support_counts.get(item) >= min_support_count or item == '_'] for itemset in sequence] for sequence in item_sequences]
	return remove_empty_elements(filtered_item_sequences) # return the new sequence database

def r_prefix_span(base_item, item_sequences, mis_count):
	# get the frequent items and construct length one frequent sequences from them
	freq_item_sequences = remove_infrequent_items(item_sequences, mis_count)
	# print('remove infrequent items', freq_item_sequences)
	frequent_items = sorted(list(set(itertools.chain(*(itertools.chain(*freq_item_sequences))))))
	# print('frequent_items_sequences', frequent_items)
	del freq_item_sequences

	#get length-1 frequent sequences
	len_1_freq_sequences = [ [[item]] for item in frequent_items]

	#remove the infrequent items
	item_sequences = remove_infrequent_items(item_sequences, mis_count)

	# add the base_item 1_length sequential patter to the output database
	if has_item(len_1_freq_sequences, base_item):
		output_patterns.append(([[base_item]], support_count(item_sequences, base_item)))
	for freq_sequence in len_1_freq_sequences:
		# print('freq_sequence', freq_sequence)
		prefix_span(freq_sequence, item_sequences, base_item, mis_count)

def begin_msps(sequences, mis_values, sdc):
	if (sequences == None or len(sequences) == 0 or mis_values == None or len(mis_values) == 0):
		print('Invalid data sequence or minimun support values')
		return
	# total number of sequence
	sequence_count = len(sequences)
	# Get the item support for each item i.e. sup(i)
	global actual_supports
	flattened_sequences = [list(set(itertools.chain(*sequence))) for sequence in sequences]
	support_counts = dict(Counter(item for flattened_sequence in flattened_sequences for item in flattened_sequence))
	actual_supports = {item:support_counts.get(item)/float(sequence_count) for item in support_counts.keys()}
	del flattened_sequences 
	# get the sorted list of frequent items i.e. items with sup(i) >= MIS(i)
	frequent_items = sorted([item for item in actual_supports.keys() if actual_supports.get(item) >= mis_values.get(item)], key = mis_values.get)
	#get count for frequent items
	for item in frequent_items:
		mis_count = int(math.ceil(mis_values.get(item)*sequence_count))
		# print('Current item', item, 'MIS count:', mis_count, 'minsup:', mis_values.get(item), 'support count:', support_counts.get(item))
		item_sequences = [sdc_filter_on_item(sequence, item, actual_supports.get(item), actual_supports, sdc) for sequence in sequences if has_item(sequence, item)]
		# print('ItemSeq:')
		# print('\n'.join([str(sequence) for sequence in item_sequences]))


		# run the restricted prefix span to get sequential pattern
		r_prefix_span(item, item_sequences, mis_count)

		# remove the item from original sequences
		sequences = remove_item(sequences, item)	

	# End of mining algorithm, print outpu
	write_output(output_patterns)

# ------------------------------reading data and trimming data------------------------------------------------------------
readData = open('data.txt','r').read()
dir_path = os.path.dirname(os.path.realpath('data.txt'))
global output_patterns, out_file, sdc
output_patterns = []
out_file = dir_path + '\output.txt'
readDataClean = readData.replace('<{','').replace('}>','') # when you use split function, it uses "," to represent after spliting, you have 2 elments.
sequences = readDataClean.split('\n')
sequences = [sequence.split('}{') for sequence in sequences]
sequences = [[[item.strip() for item in itemset.split(',')] for itemset in sequence] for sequence in sequences]
sequences = [[sorted(itemset) for itemset in sequence] for sequence in sequences]
readMIS = open('para.txt','r').read()
mis_values = { match[0]: float(match[1]) for match in re.findall(r'MIS\((\w+)\)\s+=\s+(\d*\.?\d*)', readMIS)}
sdc = float(re.search(r'SDC\s=\s(\d*\.?\d*)', readMIS).group(1))

# ------------------------------reading data and trimming data------------------------------------------------------------

# run multiple support prefix span algorithm
begin_msps(sequences, mis_values, sdc)
