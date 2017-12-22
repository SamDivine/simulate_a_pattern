# -*- coding: utf-8 -*-

from __future__ import division, print_function


class Node(object):
	def __init__(self, x, y, width, height, depth, min_size):
		self.x = x
		self.y = y
		self.width = width
		self.height = height
		self.depth = depth
		self.min_size = min_size
		self.children = list()
		self.items = list()

	@property
	def is_leaf(self):
		return (not self.children)

	def add_children_nodes(self):
		if self.children:
			return True
		children_width = self.width/2
		children_height = self.height/2
		if children_height >= self.min_size or children_width >= self.min_size:
			self.children.extend([
					Node(self.x, self.y, children_width, children_height, self.depth+1, self.min_size),
					Node(self.x+children_width, self.y, children_width, children_height, self.depth+1, self.min_size),
					Node(self.x, self.y+children_height, children_width, children_height, self.depth+1, self.min_size),
					Node(self.x+children_width, self.y+children_height, children_width, children_height, self.depth+1, self.min_size)
				])
			return True
		else:
			return False

	def generate_tree(self):
		self.add_children_nodes()
		for child in self.children:
			child.generate_tree()


	def intersect(self, x, y):
		return self.x <= x < self.x+self.width and self.y <= y < self.y+self.height

	def find_items(self, x, y):
		leaf = self.find_leaf(x, y)
		if leaf is None:
			return None
		else:
			return leaf.items

	def find_leaf(self, x, y):
		selected_node = self
		while True:
			if not selected_node.intersect(x, y):
				return None
			if selected_node.is_leaf:
				return selected_node
			else:
				for child in selected_node.children:
					if child.intersect(x, y):
						selected_node = child
						break
				else:
					raise RuntimeError("No child intersect point({}, {}), tree generation may be wrong".format(x, y))
				continue

	def add_item(self, item):
		x, y = item.x, item.y
		leaf = self.find_leaf(x, y)
		if leaf is None:
			return False
		else:
			leaf.items.append(item)
			return True

	def __repr__(self):
		return "Node<x={x}, y={y}, width={width}, height={height}, depth={depth}, min_size={min_size}".format(x=self.x, y=self.y, width=self.width, height=self.height, depth=self.depth, min_size=self.min_size)

	def print_tree(self):
		print("{tab}{info}".format(tab="  "*self.depth, info=self))
		for child in self.children:
			child.print_tree()

if __name__ == "__main__":
	a = Node(1, 2, 3, 4, 0, 0.3)
	print(a.is_leaf)
	a.add_children_nodes()
	print(a.is_leaf)
	a.generate_tree()
	a.print_tree()
	leaf = a.find_leaf(1.5, 5.5)
	print(leaf)

