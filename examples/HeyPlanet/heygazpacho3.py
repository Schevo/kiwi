#!/usr/bin/env python
from Kiwi2 import Views
from Kiwi2.initgtk import gtk, quit_if_last

class MyView(Views.GazpachoView):
    widgets = ["the_label"]   # widgets list
    def __init__(self):
        Views.GazpachoView.__init__(self,
                                    gladefile="hey", 
                                    delete_handler=quit_if_last)
        text = self.the_label.get_text() # attached by constructor
        self.the_label.set_markup('<b>%s</b>' % text)
        self.the_label.set_use_markup(True)        
        self.set_title("Avi's declaration") # change window title

app = MyView()
app.show()
gtk.main()