#!/usr/bin/env python
from Kiwi2 import Views
from Kiwi2.initgtk import gtk, quit_if_last
from Kiwi2.Widgets import ComboBox

from sets import Set

def load_colors():
    filename = "/usr/X11R6/etc/X11/rgb.txt"
    try:
        lines = file(filename).readlines()
        # the first line we don't want
        lines = lines[1:]
        s = Set([c.strip().split('\t')[2] for c in lines])
        if '' in s: s.remove('')
        return list(s)
    except IOError:
        return ['red', 'blue', 'yellow', 'green']

class Color:
    pass

class FavouriteColor(Views.BaseView):
    def __init__(self):
        win = gtk.Window()
        win.set_title("Silly question")
        win.set_border_width(12)
        label = gtk.Label("What is your favourite color?")
        box = gtk.VBox(spacing=6)
        box.pack_start(label, False)
        self.combo = ComboBox()
        self.combo.set_property('model-attribute', 'color')
        box.pack_start(self.combo, False)
        win.add(box)
        Views.BaseView.__init__(self, toplevel=win, 
                                delete_handler=quit_if_last)


the_color = Color()
app = FavouriteColor()
app.add_proxy(the_color, ['combo'])
# we need to call prefill after adding the proxy or we won't get the changes
app.combo.prefill(load_colors(), sort=True)
app.show_all()
gtk.main()
print the_color.color
