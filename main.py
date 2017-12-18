# -*- coding: utf-8 -*-

from __future__ import division
import os

import graphics
from math import tan, radians, sin, cos
import random
import time

random.seed(time.time())

canvas_width = 400
canvas_height = 400

random_x_range = 400
random_y_range = 400

a = 4
b = 4
c = 4
d = 4
r1 = 1
r2 = 1
alpha = 30
beta = 30
p1 = 0.4
p2 = 0.4
p3 = 0.2
M = 1
N = 100

def dtan(d):
	return tan(radians(d))

def dsin(d):
	return sin(radians(d))

def dcos(d):
	return cos(radians(d))

class BaseP(object):
	def __init__(self, idx, x, y, r, parent=None):
		self.x = x
		self.y = y
		self.r = r
		self.idx = idx
		self.parent = parent
		self.n = 0 if parent is None else self.next_n(parent)

	def next_n(self, parent):
		return parent.n

class Ball(BaseP):
	def __init__(self, idx, x, y, parent=None):
		super(Ball, self).__init__(idx, x, y, r1, parent)

class Node(BaseP):
	def __init__(self, idx, x, y, parent=None):
		super(Node, self).__init__(idx, x, y, r2, parent)

class Line(object):
	def __init__(self, parent, child):
		self.x1 = parent.x
		self.x2 = child.x
		self.y1 = parent.y
		self.y2 = child.y

class Simulator(object):
	def __init__(self, a, b, c, d, r1, r2, alpha, beta, p1, p2, p3, M, N):
		self.a = a
		self.b = b
		self.c = c
		self.d = d
		self.r1 = r1
		self.r2 = r2
		self.alpha = alpha
		self.beta = beta
		self.p1 = p1
		self.p2 = p2
		self.p3 = p3
		self.n = 0
		self.M = M
		self.N = N
		self.to_generate = list()
		self.trees = list()
		self.all_p = list()
		self.lines = list()
		for m in xrange(self.M):
			self.trees.append(list())

	def generate_first(self):
		random_x_list = random.sample(range(random_x_range), self.M)
		random_y_list = random.sample(range(random_y_range), self.M)
		for m in xrange(self.M):
			ball = Ball(m, random_x_list[m], random_y_list[m])
			self.to_generate.append(ball)
			self.trees[m].append(ball)
			self.all_p.append(ball)

	def get_choice(self):
		choice = random.random()
		if 0 <= choice < p1:
			return 0
		elif p1 <= choice < p1+p2:
			return 1
		else:
			return 2

	def get_new_pos(self, parent, dis, degree):
		x, y = parent.x, parent.y
		return x + dis*dcos(degree), y+dis*dsin(degree)

	def distance_square(self, p1, p2):
		x_diff = p1.x-p2.x
		y_diff = p1.y-p2.y
		return x_diff*x_diff+y_diff*y_diff

	def check_position(self, point):
		for idx in xrange(self.M):
			if idx == point.idx:
				continue
			for p in self.trees[idx]:
				if self.distance_square(point, p) < self.d*self.d:
					return False
		same_tree_d = max(self.a, self.b, self.c)
		for p in self.trees[point.idx]:
			if p is not point.parent and self.distance_square(point, p) < same_tree_d*same_tree_d:
				return False
		return True

	def get_new_p(self, parent, cls):
		x, y, idx = parent.x, parent.y, parent.idx
		point = cls(parent.idx, parent.x, parent.y, parent)
		n = point.n
		rand = random.random()
		if rand < 0.5:
			degree = n+alpha
			dis = b
		else:
			degree = n-beta
			dis = c
		point.x, point.y = self.get_new_pos(parent, dis, degree)
		return point

	def get_new_ball(self, parent):
		return self.get_new_p(parent, Ball)

	def get_new_node(self, parent):
		return self.get_new_p(parent, Node)

	def add_ball(self, parent):
		ball = self.get_new_ball(parent)
		idx = ball.idx
		if self.check_position(ball):
			self.lines.append(Line(parent, ball))
			self.trees[idx].append(ball)
			self.to_generate.append(ball)
			self.all_p.append(ball)

	def add_node(self, parent):
		node = self.get_new_node(parent)
		x, y, idx = node.x, node.y, node.idx
		b1 = Ball(idx, x, y, node)
		b2 = Ball(idx, x, y, node)
		n1 = b1.n
		n2 = b2.n
		b1.x, b1.y = self.get_new_pos(node, b, n1+alpha)
		b2.x, b2.y = self.get_new_pos(node, c, n2-beta)
		if self.check_position(b1) and self.check_position(b2):
			self.lines.extend([Line(parent, node), Line(node, b1), Line(node, b2)])
			self.trees[idx].extend([node, b1, b2])
			self.to_generate.extend([b1, b2])
			self.all_p.extend([node, b1, b2])

	def just_remove(self, parent):
		pass

	def generate_it(self):
		while len(self.to_generate) > 0 and len(self.all_p) <= N:
			g_idx = random.randint(0, len(self.to_generate)-1)
			choice = self.get_choice()
			point = self.to_generate[g_idx]
			if choice == 0:
				self.add_ball(point)
			elif choice == 1:
				self.add_node(point)
			else:
				self.just_remove(point)
			self.to_generate.pop(g_idx)

def close_enough(n1, n2, rel_tol=1e-09, abs_tol=0.0):
	return abs(n1-n1) <= max(rel_tol*max(abs(a), abs(b)), abs_tol)

def check_generation():
	s = Simulator(a, b, c, d, r1, r2, alpha, beta, p1, p2, p3, M, N)
	assert close_enough(p1+p2+p3, 1.0), "sum of 3 possibilities should be 1"
	print("Equal")
	s.generate_first()
	s.generate_it()
	print(len(s.all_p))
	print(len(s.to_generate))
	print(len(s.lines))
	


def main():
	win = GraphWin("CSSA", canvas_width, canvas_height)
	cir = Circle(Point(100, 100), 70)
	cir.draw(win)
	cir.setOutline("black")
	cir.setFill("black")

	win.getMouse()
	a = raw_input("press any key to shutdown")
	#win.close()

if __name__ == "__main__":
	check_generation()
