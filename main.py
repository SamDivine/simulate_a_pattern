# -*- coding: utf-8 -*-

from __future__ import division
import os

import graphics
from math import tan, radians, sin, cos, degrees, atan, pi
import random
import time

random.seed(time.time())

max_width = 1200
max_height = 675

random_x_range = (0, 200)
random_y_range = (0, 200)

config = {
	"t": 2000,
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
	"M": 40,
	"N": 2000,
}

def new_nv(x, y):
	t = config["t"]
	return (cos((x-pi/2)/t), (pi/2-x)/t*cos(y/t))

background_color = "white"
circle_color = "black"
line_color = "black"
line_weight = 1

def close_enough(n1, n2, rel_tol=1e-09, abs_tol=0.0):
	return abs(n1-n2) <= max(rel_tol*max(abs(n1), abs(n2)), abs_tol)

def dtan(d):
	return tan(radians(d))

def dsin(d):
	return sin(radians(d))

def dcos(d):
	return cos(radians(d))

class Vector(object):
	def __init__(self, x, y):
		self.x = x
		self.y = y

	@property
	def degree(self):
		if close_enough(self.x, 0.0):
			if close_enough(self.y, 0.0):
				raise RuntimeError("please tell me what's direction of vector (0,0)...")
			if self.y > 0:
				return 90.0
			if self.y < 0:
				return -90.0
		ret = degrees(atan(self.y/self.x))
		if self.x < 0:
			ret = ret + 180.0
		return ret

class BaseP(object):
	def __init__(self, idx, x, y, r, parent=None):
		self.x = x
		self.y = y
		self.r = r
		self.idx = idx
		self.parent = parent
		self.is_endpoint = True
		self.is_node = False

	@property
	def n(self):
		return self.nv.degree

	@property
	def nv(self):
		return Vector(*(new_nv(self.x, self.y)))

class Ball(BaseP):
	def __init__(self, idx, x, y, parent=None):
		super(Ball, self).__init__(idx, x, y, config["r1"], parent)

class Node(BaseP):
	def __init__(self, idx, x, y, parent=None):
		super(Node, self).__init__(idx, x, y, config["r2"], parent)
		self.is_node = True

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
		for m in xrange(self.M):
			while True:
				ball = Ball(m, random.randrange(*random_x_range), random.randrange(*random_y_range))
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

	def get_new_p(self, parent, cls, dis):
		x, y, idx = parent.x, parent.y, parent.idx
		point = cls(parent.idx, parent.x, parent.y, parent)
		n = parent.n
		rand = random.random()
		if rand < 0.5:
			degree = n+self.beta
		else:
			degree = n-self.beta
		point.x, point.y = self.get_new_pos(parent, dis, degree)
		return point

	def get_new_ball(self, parent):
		return self.get_new_p(parent, Ball, self.c)

	def get_new_node(self, parent):
		return self.get_new_p(parent, Node, self.a)

	def add_ball(self, parent):
		ball = self.get_new_ball(parent)
		idx = ball.idx
		if self.check_position(ball):
			parent.is_endpoint = False
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
		n = node.n
		b1.x, b1.y = self.get_new_pos(node, self.b, n+self.alpha)
		b2.x, b2.y = self.get_new_pos(node, self.b, n-self.alpha)
		if self.check_position(node) and self.check_position(b1) and self.check_position(b2):
			parent.is_endpoint = False
			node.is_endpoint = False
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
		addition_bound = 2*max(self.r1, self.r2)
		graph_height = self.max_y-self.min_y + 2*addition_bound
		graph_width = self.max_x-self.min_x + 2*addition_bound
		width = max_width
		height = int(width/graph_width*graph_height)
		if height > max_height:
			width = width/height * max_height
			height = max_height
		win = graphics.GraphWin(title, width, height)
		win.setBackground(background_color)
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

	def collect_data(self):
		self.save_csv("x")
		self.save_csv("y")
		self.save_points()
		self.save_lines()

	def save_points(self):
		endpoints = 0
		nodes = 0
		with open("points.csv", "wb") as fp:
			points_info_list = list()
			for p in self.all_p:
				if p.is_endpoint is True:
					endpoints += 1
				if p.is_node is True:
					nodes += 1
				points_info_list.append("{},{},{},{},{}".format(p.x, p.y, p.r, p.n, p.idx))
			write_list = ["{},{},{}".format(len(self.all_p), nodes, endpoints)] + points_info_list
			fp.write("\n".join(write_list))

	def save_lines(self):
		with open("lines.csv", "wb") as fp:
			for line in self.lines:
				fp.write("{}, {}, {}, {}\n".format(line.x1, line.y1, line.x2, line.y2))
		
	def save_csv(self, axis_name):
		x_list = sorted(self.all_p, key=lambda p: getattr(p, axis_name))
		filename = "{name}N{name}.csv".format(name=axis_name)
		min_v = getattr(self, "min_{}".format(axis_name))
		max_v = getattr(self, "max_{}".format(axis_name))
		with open(filename, "wb") as fp:
			nv = 0
			p_idx = 0
			iter_v = 0
			while True:
				while p_idx < len(x_list) and getattr(x_list[p_idx], axis_name) < iter_v+min_v:
					nv += 1
					p_idx += 1
				fp.write("{},{}\n".format(iter_v, nv))
				if iter_v+min_v > max_v:
					break
				iter_v += 1


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
	s.collect_data()
	s.draw("test")

if __name__ == "__main__":
	check_generation()
