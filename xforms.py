#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  xforms.py
#  
#  Copyright 2014 John Coppens <john@jcoppens.com>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  

import gtk
import pygtk
import pdb
from   goocanvas import *
import numpy as np

IMG_AREA_W = 400
IMG_AREA_H = 400
X0 = IMG_AREA_W / 2
Y0 = IMG_AREA_H / 2

SCALE = 20
AXISLENGTH = 5

class Figure():
    def __init__(self):
        self.verts = [[1, 0, 1], [-1, 0, 1], [-1, 0, -1], [1, 0, -1],
                      [1, 1, 1], [-1, 1, 1], [-1, 1, -1], [1, 1, -1],
                      [0, 2, 1], [0, 2, -1]]

        self.links = [(0, 1), (1, 2), (2, 3), (3, 0),
                      (0, 4), (1, 5), (2, 6), (3, 7),
                      (4, 8), (8, 5), (6, 9), (9, 7),
                      (4, 5), (6, 7)]

        xform = np.identity(4)

    def load_verts_from_file(self, fname):
        pass

    def load_links_from_file(self, fname):
        pass

    def rotation_matrix(self, angle):
        pass

    def translation_matrix(self, dx, dy, dz):
        m = np.identity(4)
        m[0, 3] = dx
        m[1, 3] = dy
        m[2, 3] = dz
        return m
        
    def scale_matrix(self, factor):
        return np.diag([factor, factor, factor, 1.0])

    def reset(self):
        xform = np.identity(4)

    def get_points(self):
        lst = []
        for l in self.links:
            lst.append((self.verts[l[0]], 
                        self.verts[l[1]]))
        return lst

class MainWindow(gtk.Window):
    def __init__(self):
        self.fig = None
        gtk.Window.__init__(self)
        self.connect("delete-event", self.on_delete_event)

        # At the right, box for controls
        self.r_vbox = gtk.VBox()
        self.r_vbox.set_spacing(4)
        
        reset_btn = gtk.Button("Reset")
        reset_btn.connect("clicked", self.reset_button_clicked)
        self.r_vbox.pack_start(reset_btn, fill = False, expand = False)

        lbl = gtk.Label("")
        self.r_vbox.pack_start(lbl, expand = True, fill = True)

        quit_btn = gtk.Button("Quit")
        quit_btn.connect("clicked", self.quit_button_clicked)
        self.r_vbox.pack_start(quit_btn, fill = False, expand = False)

        # At the left, a canvas for the drawing
        self.canvas = Canvas()
        self.canvas.set_size_request(IMG_AREA_W, IMG_AREA_H)
        self.canvas_root = self.canvas.get_root_item()

        canvas_scrw = gtk.ScrolledWindow()
        canvas_scrw.add(self.canvas)
        self.canvas.connect("button-press-event", self.button_press_event, None)
        self.canvas.connect("button-release-event", self.button_release_event, None)
        self.canvas.connect("motion-notify-event", self.motion_notify_event, None)

        # Put them together in the window
        hbox = gtk.HBox()
        hbox.set_spacing(4)
        hbox.pack_start(canvas_scrw, expand = True)
        hbox.pack_start(self.r_vbox)

        self.add(hbox)
        
        self.show_all()

    def run(self):
        gtk.main()

    def set_figure(self, fig):
        self.fig = fig
        self.draw_figure(self.fig)

    def quit_button_clicked(self, btn):
        gtk.mainquit()

    def reset_button_clicked(self, btn):
        """ Reset transforms """
        self.fig.reset()

    def on_delete_event(self, window, event):
        gtk.mainquit()

    def to_x(self, x):
        return X0 + x * SCALE
        
    def to_y(self, y):
        return Y0 - y * SCALE

    def axis(self):
        x_axis = polyline_new_line(self.canvas_root,
                    self.to_x(0), self.to_y(0),
                    self.to_x(AXISLENGTH), self.to_x(0),
                    stroke_color = "blue",
                    line_width = 1.0)
        
        y_axis = polyline_new_line(self.canvas_root,
                    self.to_x(0), self.to_y(0),
                    self.to_x(0), self.to_y(AXISLENGTH),
                    stroke_color = "green",
                    line_width = 1.0)

    def draw_figure(self, fig):
        for line in fig.get_points():
            polyline_new_line(self.canvas_root,
                    self.to_x(line[0][0]), self.to_y(line[0][1]),
                    self.to_x(line[1][0]), self.to_y(line[1][1]),
                    stroke_color = "red",
                    line_width = 1.0)

    def test_box(self):
        rect = Rect(parent = self.canvas_root,
                    x = 10, y = 10, width = 380, height = 390,
                    line_width = 1.0)

    def d_to_degrees(self, d):
        return 0.5 * d

    def d_to_scale(self, d):
        scale = 1.0 + 0.01 * abs(d)
        if d >= 0:
            return scale
        else:
            return 1.0 / scale

    def button_press_event(self, canvas, event, data):
        print event
        self.mouse_button = event.button
        self.x_press_at = event.x
        self.y_press_at = event.y

    def button_release_event(self, canvas, event, data):
        dx = event.x - self.x_press_at
        dy = event.y - self.y_press_at
        if self.mouse_button == 1:
            print "Moving", dx, dy
        elif self.mouse_button == 2:
            print "Rotating", self.d_to_degrees(dx), self.d_to_degrees(dy)
        elif self.mouse_button == 3:
            print "Scaling", self.d_to_scale(dx)
        self.button = None
        
    def motion_notify_event(self, canvas, event, data):
        pass

def main():
    w = MainWindow()
    #w.test_box()
    f = Figure()
    print f.scale_matrix(0.5)
    w.axis()
    w.set_figure(f)
    
    w.run()
    return 0

if __name__ == '__main__':
    main()

