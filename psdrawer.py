# -*- coding: utf-8 -*-

import psfile

str_color_map = {
	"black": "0 0 0",
	"red": "1 0 0",
	"green": "0 1 0",
	"blue": "0 0 1",
	"white": "1 1 1",
}

class PsDrawer(object):
	def __init__(self, filename, width, height):
		self.fd = psfile.EPSFile(filename, width, height)

	def get_color_str(self, color_name):
		if not color_name in str_color_map.keys():
			color_name = "black"
		return str_color_map[color_name]

	def change_color(self, color_name="black"):
		color_str = self.get_color_str(color_name)
		fd = self.fd
		fd.append("{} setrgbcolor".format(color_str))

	def set_background(self, color_name="white"):
		color_str = self.get_color_str(color_name)
		fd = self.fd
		fd.append("{} setrgbcolor".format(color_str))
		fd.append("0 0 {} {} rectfill".format(fd.width, fd.height))

	def draw_line(self, x1, y1, x2, y2, weight, modify_color=False, color_name="black"):
		color_str = self.get_color_str(color_name)
		fd = self.fd
		if modify_color is True:
			fd.append("{} setrgbcolor".format(color_str))
		fd.append("%.2f setlinewidth" % weight)
		fd.append("%.5f %.5f moveto" % (x1, y1))
		fd.append("%.5f %.5f lineto" % (x2, y2))
		fd.append("stroke")

	def draw_circle(self, x, y, r, modify_color=False, outline_color="black", fill_color="black"):
		ol_color = self.get_color_str(outline_color)
		f_color = self.get_color_str(fill_color)
		fd = self.fd
		if modify_color is True:
			fd.append("{} setrgbcolor".format(ol_color))
		fd.append("%.5f %.5f %.5f 0 360 arc" % (x, y, r))
		if modify_color is True:
			fd.append("{} setrgbcolor".format(f_color))
		fd.append("fill")
		fd.append("stroke")

	def close(self):
		self.fd.close()


if __name__ == "__main__":
	pd = PsDrawer("test.eps", 400, 400)
	line_weight = 2
	pd.draw_circle(100, 100, 50)
	pd.draw_line(200, 200, 300, 300, line_weight)
	pd.close()
