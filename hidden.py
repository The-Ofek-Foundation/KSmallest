import random

NUM_ELEMENTS = 10000
K = 40

_LIST = list(range(NUM_ELEMENTS))
random.shuffle(_LIST)

_num_comparisons = 0

def COMPARE(index1: int, index2: int) -> bool:
	global _num_comparisons
	_num_comparisons += 1
	return _LIST[index1] < _LIST[index2]

def get_num_comparisons() -> int:
	return _num_comparisons

# used only for debugging / verifying purposes
def GET(index: int) -> int:
	if index < 0:
		return -1

	return _LIST[index]

def reset():
	global _LIST, _num_comparisons
	random.shuffle(_LIST)
	_num_comparisons = 0
