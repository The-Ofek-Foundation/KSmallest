from hidden import COMPARE, GET_LIST

from collections import namedtuple, defaultdict

import functools

SortData = namedtuple('SortData', ('greater_than', 'less_than'))

class SmartCompare(object):
	def __init__(self):
		self._data = defaultdict(lambda : SortData(set(), set()))

	def set_less_than(self, a: int, b: int):
		# a is not only less than b, it's also less than everything that b is less than
		self._data[a].less_than.add(b)
		self._data[a].less_than.update(self._data[b].less_than)
		for elem in self._data[a].greater_than:
			self._data[elem].less_than.update(self._data[a].less_than)

		self._data[b].greater_than.add(a)
		self._data[b].greater_than.update(self._data[a].greater_than)
		for elem in self._data[b].less_than:
			self._data[elem].greater_than.update(self._data[b].greater_than)

	def set_greater_than(self, a: int, b: int):
		self.set_less_than(b, a)

	# returns true if a is less than b
	def compare(self, a: int, b: int) -> bool:
		if b in self._data[a].less_than:
			return True

		if b in self._data[a].greater_than:
			return False

		# we don't already know, we must do a real comparison
		a_less_than_b = COMPARE(a, b)
		if a_less_than_b:
			self.set_less_than(a, b)
		else:
			self.set_greater_than(a, b)

		return a_less_than_b

	def sort_key(self) -> 'lambda':
		return functools.cmp_to_key(lambda a, b: -1 if self.compare(a, b) else 1)

	def __str__(self) -> str:
		return str(dict(self._data))


# sorting average # of comparisons:
# smart built-in  sort: 133 comparisons
# smart hybrid 4  sort: 138 comparisons
# smart merge     sort: 139 comparisons
# dumb  hybrid 4  sort: 154 comparisons
# dumb  merge     sort: 156 comparisons
# dumb  built-in  sort: 157 comparisons
# smart insertion sort: 237 comparisons
# dumb  insertion sort: 244 comparisons
#
# hybrid sort is merge sort that switches to insertion.
# hybrid 4 means switch to insertion whenever sorting <= 4 items

# code taken from geeks for geeks website
def smart_insertion_sort(elements: [int], sc: SmartCompare, low: int = 0, high: int = -1):
	if high == -1:
		high = len(elements)

	for i in range(low + 1, high):
		key = elements[i]

		j = i - 1
		while j >= low and sc.compare(key, elements[j]):
			elements[j + 1] = elements[j]
			j -= 1

		elements[j + 1] = key

# code inspired from geeks for geeks website
def smart_merge(elements: [int], sc: SmartCompare, low: int, mid: int, high: int):
	lower_elements = elements[low:mid]
	higher_elements = elements[mid:high]

	lower_index = higher_index = 0
	merged_index = low

	while lower_index < len(lower_elements) and higher_index < len(higher_elements):
		if sc.compare(lower_elements[lower_index], higher_elements[higher_index]):
			elements[merged_index] = lower_elements[lower_index]
			lower_index += 1
		else:
			elements[merged_index] = higher_elements[higher_index]
			higher_index += 1

		merged_index += 1

	for elem in lower_elements[lower_index:] + higher_elements[higher_index:]:
		elements[merged_index] = elem
		merged_index += 1


# code inspired from geeks for geeks website
def smart_hybrid_merge_sort(elements: [int], sc: SmartCompare, low: int = 0, high: int = -1, hybrid_cutoff: int = 4):
	if high == -1:
		high = len(elements)

	if low >= high - 1:
		return

	if high - low <= hybrid_cutoff:
		smart_insertion_sort(elements, sc, low, high)
		return

	mid = (low + high) // 2
	smart_hybrid_merge_sort(elements, sc, low, mid, hybrid_cutoff)
	smart_hybrid_merge_sort(elements, sc, mid, high, hybrid_cutoff)
	smart_merge(elements, sc, low, mid, high)

def smart_binary_search(elements: [int], sc: SmartCompare, val: int, low: int, high: int) -> int:
	while high > low:
		mid = (high + low) // 2

		if sc.compare(val, elements[mid]):
			high = mid
		else:
			low = mid + 1

	return high