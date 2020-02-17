from hidden import NUM_ELEMENTS, K, COMPARE, get_num_comparisons, GET, reset, PRINT_LIST, GET_LIST
from tourneytree import Position, TourneyTree
from smartcompare import SortData, SmartCompare, smart_hybrid_merge_sort, smart_insertion_sort, smart_merge, smart_binary_search

import random

def _populate_lowest(tt: TourneyTree):
	num_unused_leaves_left = tt.num_unused_leaves
	curr_num = 0

	for index in range(tt.size):
		if index & 1 == 1 and num_unused_leaves_left > 0:
			# set to unused leaf
			num_unused_leaves_left -= 1
			tt[Position(row = 0, index = index)] = -1
			continue

		tt[Position(row = 0, index = index)] = curr_num
		curr_num += 1

def _populate_row(tt: TourneyTree, row: int):
	for pos in tt.iter_row(row):
		children = tt.get_children(pos)

		if len(children) == 1:
			tt[pos] = tt[children[0]]
			continue

		if len(children) == 0:
			tt[pos] = -1
			continue

		if len(children) != 2:
			raise Exception("should only be one or two children")

		tt[pos] = tt[children[0]] if COMPARE(tt[children[0]], tt[children[1]]) else tt[children[1]]

def _populate_table(tt: TourneyTree):
	_populate_lowest(tt)

	for row in range(1, tt.height):
		_populate_row(tt, row)

# removes a node and returns the replaced value
def _remove_node(tt: TourneyTree, pos: Position) -> int:
	children = tt.get_children(pos)
	val = tt[pos]

	if len(children) == 0:
		tt[pos] = -1
		return -1

	if len(children) == 1:
		new_val = _remove_node(tt, children[0])

		tt[pos] = new_val
		return new_val

	same_child = tt.get_same_child(pos)
	other_child = tt.get_sibling(same_child)
	other_val = tt[other_child]

	new_same_val = _remove_node(tt, same_child)
	if new_same_val == -1:
		tt[pos] = other_val
		return other_val

	tt[pos] = new_same_val if COMPARE(new_same_val, other_val) else other_val
	return tt[pos]

def _remove_top(tt: TourneyTree):
	_remove_node(tt, tt.top())


def _run(tt: TourneyTree, k: int) -> [int]:
	_populate_table(tt)

	ksmallest = list()
	for i in range(k):
		ksmallest.append(tt[tt.top()])

		if i < k - 1:
			_remove_top(tt)


	return GET_LIST(ksmallest)

# on average 23.5 of the actual k smallest will be in this sample
def _guess_k_smallest(tt: TourneyTree, k: int) -> [int]:
	ksmallest_guess = list()
	for row in range(tt.height - 1, -1, -1):
		for pos in tt.iter_row(row):
			if tt[pos] not in ksmallest_guess:
				ksmallest_guess.append(tt[pos])

			if len(ksmallest_guess) == k:
				return ksmallest_guess

	return ksmallest_guess

# on average 25.5 of the actual k smallest will be in this sample
def _guess_k_smallest_2(tt: TourneyTree, k: int) -> [int]:
	# item: (row on, row of partner)
	row_scores = dict()
	row_scores[tt[tt.top()]] = (tt.height - 1, tt.height - 1)

	for row in range(tt.height - 2, -1, -1):
		for pos in tt.iter_row(row):
			if tt[pos] not in row_scores:
				row_scores[tt[pos]] = (row, row_scores[tt[tt.get_sibling(pos)]][0])

		if len(row_scores) >= k:
			return sorted(row_scores, key=row_scores.__getitem__, reverse=True)[:k]

	return sorted(row_scores, key=row_scores.__getitem__, reverse=True)[:k]

# max 25.5 depending on constant
def _guess_k_smallest_3(tt: TourneyTree, k: int) -> [int]:
	# item: (row on, row of partner)
	row_scores = dict()
	row_scores[tt[tt.top()]] = (tt.height - 1, tt.height - 1)

	sort_by = dict()
	sort_by[tt[tt.top()]] = 2 * (tt.height - 1)

	for row in range(tt.height - 2, -1, -1):
		for pos in tt.iter_row(row):
			if tt[pos] not in row_scores:
				row_scores[tt[pos]] = (row, row_scores[tt[tt.get_sibling(pos)]][0])
				# you can weight this 0.001 constant differently
				# doesn't seem fruitful though
				sort_by[tt[pos]] = row + 0.001 * row_scores[tt[tt.get_sibling(pos)]][0]

	return sorted(row_scores, key=sort_by.__getitem__, reverse=True)[:k]

def _get_element_positions(tt: TourneyTree, elements: [int]) -> {int: Position}:
	elements_left = set(elements)
	element_positions = dict()

	for row in range(tt.height - 1, -1, -1):
		for pos in tt.iter_row(row):
			parent = tt.get_parent(pos)

			if tt[pos] not in elements_left:
				continue

			element_positions[tt[pos]] = pos
			elements_left.remove(tt[pos])

			if len(elements_left) == 0:
				return element_positions

	return element_positions

def _create_smart_compare(tt: TourneyTree, elements: [int]) -> SmartCompare:
	sc = SmartCompare()

	for element, pos in _get_element_positions(tt, elements).items():
		parent = tt.get_parent(pos)

		if not parent:
			continue

		sc.set_greater_than(tt[pos], tt[parent])

	return sc

def _evaluate_contender(tt: TourneyTree, sc: SmartCompare, val: int, contenders: [int], k: int):
	pos = _get_element_positions(tt, [val])[val]

	for child in tt.iter_same_child(pos):
		sibling = tt.get_sibling(child)
		sibling_val = tt[sibling]

		if sibling_val < 0:
			continue

		if sibling_val in contenders:
			continue

		sc.set_greater_than(sibling_val, val)

		sc.compare(sibling_val, contenders[-1])
		index = smart_binary_search(contenders, sc, sibling_val, contenders.index(val) + 1, len(contenders))
		contenders.insert(index, sibling_val)

		if len(contenders) > k:
			contenders.pop()

def _evaluate_contenders(tt: TourneyTree, sc: SmartCompare, contenders: [int], k: int):
	for i in range(k):
		_evaluate_contender(tt, sc, contenders[i], contenders, k)


def _run_method_2(tt: TourneyTree, k: int) -> [int]:
	_populate_table(tt)
	contenders = _guess_k_smallest_2(tt, K)
	sc = _create_smart_compare(tt, contenders)
	contenders.sort(key=sc.sort_key())

	_evaluate_contenders(tt, sc, contenders, k)

	ksmallest = contenders

	return GET_LIST(ksmallest)

def _test_accuracy():
	count_misses = 0
	total_trials = 1000
	total_num_comparisons = 0

	tt = TourneyTree(NUM_ELEMENTS)

	for i in range(total_trials):
		reset()
		ksmallest = _run(tt, K)
		if ksmallest != list(range(K)):
			count_misses += 1

		total_num_comparisons += get_num_comparisons()
		print(f'{i}: {count_misses} {count_misses / (i + 1) * 100:.2f} {total_num_comparisons / (i + 1):.3f}')

def _test_second_method():
	total_num_hits = total_num_comparisons = 0
	total_trials = 1000

	tt = TourneyTree(NUM_ELEMENTS)

	for i in range(total_trials):
		reset()
		ksmallest = _run_method_2(tt, K)

		total_num_hits += len([i for i in ksmallest if i < K])
		total_num_comparisons += get_num_comparisons()
		print(f'{i}: {total_num_hits / (i + 1):.3f} {total_num_comparisons / (i + 1):.3f}')

if __name__ == '__main__':
	# _test_accuracy()
	_test_second_method()

	# tt = TourneyTree(NUM_ELEMENTS)
	# less_than_10_misses = 0
	# total_trials = 100

	# for i in range(total_trials):
	# 	reset()
	# 	_populate_table(tt)
	# 	ksmallest = GET_LIST(_guess_k_smallest_2(tt, K))
	# 	num_hits = len([i for i in ksmallest if i < K])

	# 	if num_hits > 30:
	# 		less_than_10_misses += 1

	# 	print(f'{i}: {less_than_10_misses} {less_than_10_misses / (i + 1) * 100:.2f}')

	# ksmallest = _run_method_2(tt, K)
	# print(ksmallest)
	# print(get_num_comparisons())
