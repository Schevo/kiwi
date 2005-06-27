#!/usr/bin/env python
from kiwi import Delegates
from kiwi.initgtk import gtk, quit_if_last

class Hello(Delegates.Delegate):
    def __init__(self):
        self.index = 0
        self.text = [ "I've decided to take my work back underground",
                      "To keep it from falling into the wrong hands." ]

        topwidget = gtk.Window()
        topwidget.set_title("So...")
        self.button = gtk.Button(self.text[self.index])
        topwidget.add(self.button)

        Delegates.Delegate.__init__(self, topwidget, 
                                    delete_handler=quit_if_last)
        self.focus_topmost() # focus button, our only widget

    def on_button__clicked(self, button, *args):
        self.index = self.index + 1
        if self.index > 1: # Two clicks and we're gone
            self.hide_and_quit()
            return # the *handler's* return value disappears into GTK+
        button.set_label(self.text[self.index])

app = Hello()
app.show_all()
gtk.main()

