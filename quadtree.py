# -*- coding: utf-8 -*-

from __future__ import division, print_function
from collections import deque

MAX_DEPTH = 10

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

	@property
	def upper_x(self):
		return self.x+self.width

	@property
	def upper_y(self):
		return self.y+self.height

	@property
	def can_spawn(self):
		return self.depth < MAX_DEPTH and (self.height >= 2*self.min_size or self.width >= 2*self.min_size)

	def add_children_nodes(self):
		if not self.can_spawn:
			return False
		if self.children:
			return True
		children_width = self.width/2
		children_height = self.height/2
		self.children.extend([
			Node(self.x, self.y, children_width, children_height, self.depth+1, self.min_size),
			Node(self.x+children_width, self.y, children_width, children_height, self.depth+1, self.min_size),
			Node(self.x, self.y+children_height, children_width, children_height, self.depth+1, self.min_size),
			Node(self.x+children_width, self.y+children_height, children_width, children_height, self.depth+1, self.min_size)
		])
		return True

	def loop_generate(self):
		# change list to deque, now the performance is almost same as recursive_generate
		# BUT, both of these generate function face the same problem
		#        when MAX_DEPTH comes to 11, the program raise MemoryError
		# so, generating an entire tree at first may be a bad idea in some situations
		to_generate_list = deque()
		to_generate_list.append(self)
		while True:
			try:
				node = to_generate_list.popleft()
			except Exception as e:
				break
			node.add_children_nodes()
			for child in node.children:
				to_generate_list.append(child)

	def recursive_generate(self):
		# I think this is not a real recursion
		self.add_children_nodes()
		for child in self.children:
			child.recursive_generate()

	def generate_tree(self):
		self.recursive_generate()
		
	def intersect(self, x, y):
		return self.x <= x < self.upper_x and self.y <= y < self.upper_y

	def circle_intersect(self, x, y, r):
		return self.x-r <= x < self.upper_x+r and self.y-r <= y < self.upper_y+r

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

	def find_leaves(self, x, y, r):
		to_check_node = [self]
		ret = list()
		while True:
			if not to_check_node:
				break
			node = to_check_node.pop(0)
			if not node.circle_intersect(x, y, r):
				continue
			if node.is_leaf:
				ret.append(node)
				continue
			for child in node.children:
				if child.circle_intersect(x, y, r):
					to_check_node.append(child)
		return ret


	def add_item(self, item):
		x, y = item.x, item.y
		leaf = self.find_leaf(x, y)
		if leaf is None:
			return False
		else:
			leaf.items.append(item)
			return True

	def extend_items(self, items):
		for item in items:
			self.add_item(item)

	def __repr__(self):
		return "Node<x={x}, y={y}, width={width}, height={height}, depth={depth}, min_size={min_size}".format(x=self.x, y=self.y, width=self.width, height=self.height, depth=self.depth, min_size=self.min_size)

	def print_tree(self):
		print("{tab}{info}".format(tab="  "*self.depth, info=self))
		for child in self.children:
			child.print_tree()

class IncTree(Node):
	def generate_tree(self):
		print("need not call generate_tree")

	def recursive_generate(self):
		print("need not call recursive_generate")

	def loop_generate(self):
		print("need not call loop_generate")

	def add_item(self, item):
		x, y = item.x, item.y
		leaf = self.find_leaf(x, y)
		while True:
			if not leaf.can_spawn:
				leaf.items.append(item)
				break
			else:
				leaf.add_children_nodes()
				for child in leaf.children:
					if child.intersect(x, y):
						leaf = child
						break
				else:
					break

if __name__ == "__main__":
	import time
	import sys
	import os
	import psutil
	import cPickle
	#start = time.time()
	#a = Node(0, 0, 1024, 1024, 0, 0.1)
	#a.recursive_generate()
	#print(time.time()-start)
	try:
		start = time.time()
		b = Node(0, 0, 1024, 1024, 0, 0.1)
		print("Memory size of Node b is {} bytes".format(sys.getsizeof(b)))
		print("Memory size of b.children is {} bytes".format(sys.getsizeof(b.children)))
		b.loop_generate()
		print(time.time()-start)
		#print("Memory size of Node b is {} bytes".format(sys.getsizeof(b)))
		print("Memory size of b.children is {} bytes".format(sys.getsizeof(b.children)))
		print("Memory size of b.items is {} bytes".format(sys.getsizeof(b.items)))
		p_s = cPickle.dumps(b)
		print("cPickled Node b length is {}".format(len(p_s)))
		sys.exit(0)
	except Exception as e:
		print(str(e))
		sys.exit(1)
	finally:
		p = psutil.Process(os.getpid())
		mem = p.memory_info()[0]/float(2**20)
		print("memory usage: {} MB".format(mem))

