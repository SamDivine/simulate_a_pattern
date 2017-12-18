# -*- coding: utf-8 -*-

from __future__ import division
import os

import graphics
from math import tan, radians, sin, cos
import random
import time

random.seed(time.time())

canvas_width = 400
canvas_height = 800

random_x_range = 100
random_y_range = 400

config = {
	"a": 4,
	"b": 4,
	"c": 4,
	"d": 4,
	"r1": 0.5,
	"r2": 1,
	"alpha": 20,
	"beta": 15,
	"p1": 0.6,
	"p2": 0.35,
	"p3": 0.05,
	"M": 2,
	"N": 2000,
}

circle_color = "black"
line_color = "black"
line_weight = 1

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
		super(Ball, self).__init__(idx, x, y, config["r1"], parent)

class Node(BaseP):
	def __init__(self, idx, x, y, parent=None):
		super(Node, self).__init__(idx, x, y, config["r2"], parent)

class Line(object):
	def __init__(self, parent, child):
		self.x1 = parent.x
		self.x2 = child.x
		self.y1 = parent.y
		self.y2 = child.y

class Simulator(object):
	def __init__(self, conf):
		self.a = conf["a"]
		self.b = conf["b"]
		self.c = conf["c"]
		self.d = conf["d"]
		self.r1 = conf["r1"]
		self.r2 = conf["r2"]
		self.alpha = conf["alpha"]
		self.beta = conf["beta"]
		self.p1 = conf["p1"]
		self.p2 = conf["p2"]
		self.p3 = conf["p3"]
		self.n = 0
		self.M = conf["M"]
		self.N = conf["N"]

		self.max_x = float("-inf")
		self.max_y = float("-inf")
		self.min_x = float("inf")
		self.min_y = float("inf")
		self.to_generate = list()
		self.trees = list()
		self.all_p = list()
		self.lines = list()
		for m in xrange(self.M):
			self.trees.append(list())

	def modify_bound(self, *points):
		for p in list(points):
			x, y = p.x, p.y
			if x > self.max_x:
				self.max_x = x
			if x < self.min_x:
				self.min_x = x
			if y > self.max_y:
				self.max_y = y
			if y < self.min_y:
				self.min_y = y

	def generate_first(self):
		random_x_list = random.sample(range(random_x_range), self.M)
		random_y_list = random.sample(range(random_y_range), self.M)
		for m in xrange(self.M):
			while True:
				ball = Ball(m, random_x_list[m], random_y_list[m])
				for p in self.to_generate:
					if self.distance_square(ball, p) < self.d*self.d:
						break
				else:	
					self.modify_bound(ball)
					self.to_generate.append(ball)
					self.trees[m].append(ball)
					self.all_p.append(ball)
					break
		print("inited it")

	def get_choice(self):
		choice = random.random()
		if 0 <= choice < self.p1:
			return 0
		elif self.p1 <= choice < self.p1+self.p2:
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
			degree = n+self.alpha
			dis = self.b
		else:
			degree = n-self.beta
			dis = self.c
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
			self.modify_bound(ball)
			self.trees[idx].append(ball)
			self.to_generate.append(ball)
			self.all_p.append(ball)
			return True
		return False

	def add_node(self, parent):
		node = self.get_new_node(parent)
		x, y, idx = node.x, node.y, node.idx
		b1 = Ball(idx, x, y, node)
		b2 = Ball(idx, x, y, node)
		n1 = b1.n
		n2 = b2.n
		b1.x, b1.y = self.get_new_pos(node, self.b, n1+self.alpha)
		b2.x, b2.y = self.get_new_pos(node, self.c, n2-self.beta)
		if self.check_position(node) and self.check_position(b1) and self.check_position(b2):
			self.lines.extend([Line(parent, node), Line(node, b1), Line(node, b2)])
			self.modify_bound(node, b1, b2)
			self.trees[idx].extend([node, b1, b2])
			self.to_generate.extend([b1, b2])
			self.all_p.extend([node, b1, b2])
			return True
		return False

	def just_remove(self, parent):
		return True

	def generate_it(self):
		while len(self.to_generate) > 0 and len(self.all_p) <= self.N:
			g_idx = random.randint(0, len(self.to_generate)-1)
			choice = self.get_choice()
			point = self.to_generate[g_idx]
			if choice == 0:
				ret = self.add_ball(point)
			elif choice == 1:
				ret = self.add_node(point)
			else:
				ret = self.just_remove(point)

			if ret is True:
				self.to_generate.pop(g_idx)

	def draw(self, title="test"):
		#height, width = win.height, win.width
		#
		addition_bound = 2*max(self.r1, self.r2)
		graph_height = self.max_y-self.min_y + 2*addition_bound
		graph_width = self.max_x-self.min_x + 2*addition_bound
		height = canvas_height
		width = height/graph_height*graph_width
		win = graphics.GraphWin(title, width, height)
		x_scale = width/graph_width
		y_scale = height/graph_height
		point_scale = (x_scale+y_scale)/2
		for p in self.all_p:
			r = p.r*point_scale
			x = (p.x-self.min_x+addition_bound)*x_scale
			y = (p.y-self.min_y+addition_bound)*y_scale
			cir = graphics.Circle(graphics.Point(x, y), r)
			cir.draw(win)
			cir.setOutline(circle_color)
			cir.setFill(circle_color)

		for line in self.lines:
			x1 = (line.x1-self.min_x+addition_bound)*x_scale
			x2 = (line.x2-self.min_x+addition_bound)*x_scale
			y1 = (line.y1-self.min_y+addition_bound)*y_scale
			y2 = (line.y2-self.min_y+addition_bound)*y_scale
			li = graphics.Line(graphics.Point(x1, y1), graphics.Point(x2, y2))
			li.draw(win)
			li.setOutline(line_color)
			li.setFill(line_color)
			li.setWidth(line_weight)
		win.getMouse()
		a = raw_input("press any key to shutdown")




def close_enough(n1, n2, rel_tol=1e-09, abs_tol=0.0):
	return abs(n1-n1) <= max(rel_tol*max(abs(n1), abs(n2)), abs_tol)

def check_generation():
	s = Simulator(config)
	assert close_enough(s.p1+s.p2+s.p3, 1.0), "sum of 3 possibilities should be 1"
	print("Equal")
	s.generate_first()
	s.generate_it()
	print(len(s.all_p))
	print(len(s.to_generate))
	print(len(s.lines))
	print(s.max_x)
	print(s.min_x)
	print(s.max_y)
	print(s.min_y)
	s.draw("test")


def main():
	win = graphics.GraphWin("CSSA", canvas_width, canvas_height)
	#cir = Circle(Point(100, 100), 70)
	#cir.draw(win)
	#cir.setOutline("black")
	#cir.setFill("black")
	line = graphics.Line(graphics.Point(100, 100), graphics.Point(50, 50))
	line.draw(win)
	line.setOutline(line_color)
	line.setFill(line_color)
	line.setWidth(line_weight)

	win.getMouse()
	a = raw_input("press any key to shutdown")
	#win.close()

if __name__ == "__main__":
	check_generation()
	#main()
