#!/usr/bin/env python
from Kiwi import Views, mainquit

class MyView(Views.GladeView):
    widgets = [ "the_label" ]   # widgets list
    def __init__(self):
        Views.GladeView.__init__(self,
                                 gladefile="hey", 
                                 delete_handler=mainquit)
        self.the_label.set_bold()           # attached by constructor
        self.set_title("Avi's declaration") # change window title

app = MyView()
app.show_and_loop()
