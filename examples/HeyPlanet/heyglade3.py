#!/usr/bin/env python
from kiwi import Views
from kiwi.initgtk import gtk, quit_if_last

class MyView(Views.BaseView):
    widgets = ["the_label"]   # widgets list
    gladefile = "hey"
    def __init__(self):
        Views.BaseView.__init__(self, delete_handler=quit_if_last)
        text = self.the_label.get_text() # attached by constructor
        self.the_label.set_markup('<b>%s</b>' % text)
        self.the_label.set_use_markup(True)        
        self.set_title("Avi's declaration") # change window title

app = MyView()
app.show()
gtk.main()
