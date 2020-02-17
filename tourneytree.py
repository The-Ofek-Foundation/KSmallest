import math
from collections import namedtuple

from hidden import GET

Position = namedtuple('Position', ['row', 'index'])

class TourneyTree(object):
	def __init__(self, num_elements: int):

		# height of tree
		self.height = math.ceil(math.log(num_elements, 2)) + 1

		# smallest perfect power of two big enough to contain all the elements
		self.size = int(2 ** (self.height - 1))

		self.num_unused_leaves = self.size - num_elements

		# initialize the table
		self._table = list()
		num_elements_in_row = self.size

		for i in range(self.height):
			self._table.append([-1] * num_elements_in_row)
			num_elements_in_row //= 2

	def __getitem__(self, pos: Position) -> int:
		return self._table[pos.row][pos.index]

	def __setitem__(self, pos: Position, value: int):
		self._table[pos.row][pos.index] = value

	def top(self) -> Position:
		return Position(row = self.height - 1, index = 0)

	def iter_row(self, row: int) -> Position:
		if row < 0 or row >= self.height:
			return None

		for index in range(len(self._table[row])):
			yield Position(row = row, index = index)

	def get_parent(self, pos: Position) -> Position:
		if pos.row >= self.height - 1:
			return None

		return Position(row = pos.row + 1, index = pos.index // 2)

	def get_children(self, pos: Position) -> [Position]:
		if pos.row <= 0:
			return ()

		left_child = Position(row = pos.row - 1, index = pos.index * 2)
		right_child = Position(row = pos.row - 1, index = pos.index * 2 + 1)

		children = list()
		if self[left_child] >= 0:
			children.append(left_child)

		if self[right_child] >= 0:
			children.append(right_child)

		return children

	def get_sibling(self, pos: Position) -> Position:
		if pos.row == self.height - 1:
			return pos

		# 0 <-> 1, 2 <-> 3, 4 <-> 5, etc.
		return Position(row = pos.row, index = pos.index + 1 - 2 * (pos.index % 2))

	def __str__(self) -> str:
		s = ""

		for i in range(self.height):
			s += " ".join((str(GET(a)) for a in self._table[self.height - i - 1]))
			s += "\n"

		return s[:-1]
