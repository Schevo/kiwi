#!/usr/bin/env python
from Kiwi2 import Views
from Kiwi2.initgtk import gtk, quit_if_last

class HeyPlanet(Views.BaseView):
    def __init__(self):
        win = gtk.Window()
        win.set_title("I'm coming to London")
        label = gtk.Label("Anything to declare?")
        win.add(label)
        win.set_default_size(200, 50)
        Views.BaseView.__init__(self, toplevel=win, 
                                delete_handler=quit_if_last)
app = HeyPlanet()
app.show_all()
gtk.main()