from hidden import *
from tourneytree import *

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
		new_val = tt[children[0]] if tt[children[0]] != val else -1
		tt[pos] = new_val
		return new_val

	same_child, other_child = (children[0], children[1]) if tt[children[0]] == val else (children[1], children[0])
	other_val = tt[other_child]

	new_same_val = _remove_node(tt, same_child)
	if new_same_val == -1:
		tt[pos] = other_val
		return other_val

	tt[pos] = new_same_val if COMPARE(new_same_val, other_val) else other_val
	return tt[pos]

def _remove_top(tt: TourneyTree):
	_remove_node(tt, tt.top())


def _run(tt: TourneyTree, k: int):
	_populate_table(tt)

	# print(tt)
	ksmallest = list()
	for i in range(k):
		ksmallest.append(tt[tt.top()])

		if i < k - 1:
			_remove_top(tt)

		# print(tt)

	# print(ksmallest[0], GET(ksmallest[0]))

	# print(ksmallest)

	# for i in ksmallest:
	# 	print(GET(i))

	# print(get_num_comparisons())

	# print(tt._table[12])
	# for i in tt._table[13]:
	# 	print(GET(i))
	# print(len(tt._table[0]))

	return [GET(i) for i in ksmallest]

if __name__ == '__main__':
	count_misses = 0
	total_trials = 10000
	total_num_comparisons = 0

	tt = TourneyTree(NUM_ELEMENTS)

	for i in range(total_trials):
		reset()
		ksmallest = _run(tt, K)
		if ksmallest != list(range(K)):
			count_misses += 1
			print("MISS!!!")

		total_num_comparisons += get_num_comparisons()
		print(i)

	print("Miss statistics (total, %):")
	print(count_misses, (count_misses / total_trials) * 100)

	print("Average number of comparisons:")
	print(total_num_comparisons / total_trials)
	# _run(NUM_ELEMENTS, K)
	# tt = TourneyTree(8)

	# print(tt.get_parent(Position(1, 3)))
	# print(tt[Position(1, 3)])

	# print(COMPARE(1, 2))
	# print(get_num_comparisons())
	# print(COMPARE(1, 5))
	# print(get_num_comparisons())