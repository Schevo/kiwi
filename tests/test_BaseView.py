#!/usr/bin/env python
import sys
sys.path.insert(0, "..")

from Kiwi.Views import BaseView
from Kiwi.Controllers import BaseController
from Kiwi.initgtk import gtk
from gtk import keysyms

class FooView(BaseView):
    widgets = [ "vbox", "label" ]
    def __init__(self):
        self.build_ui()
        BaseView.__init__(self, delete_handler=gtk.mainquit)

    def build_ui(self):
        self.win = gtk.Window()
        vbox = gtk.VBox()
        self.label = gtk.Label("Pick one noogie")
        self.button = gtk.Button(label="Noogie!")
        vbox.add(self.button)
        self.foo__button = gtk.Button(label="Boogie!")
        vbox.add(self.foo__button)
        self.win.add(vbox)
        self.vbox = vbox
        return vbox

class FooController(BaseController):
    def __init__(self, view):
        keyactions = {
            keysyms.A: self.on_button__clicked,
            keysyms.a: self.on_button__clicked,
            keysyms.B: self.on_foo__button__clicked,
            keysyms.b: self.on_foo__button__clicked
        }
        BaseController.__init__(self, view, keyactions)

    def on_button__clicked(self, *args):
        Bar().run(self.view)

    def on_foo__button__clicked(self, *args):
        # This is subclassed
        print "Good click!"

    def run(self):
        self.view.show_all()
        gtk.mainloop()

class Bar(BaseView, BaseController):
    def __init__(self):
        self.win = gtk.Window()
        l = gtk.Label("foobar!")
        self.win.add(l)
        BaseView.__init__(self, delete_handler=gtk.mainquit)
        BaseController.__init__(self, view=self)
        self.view.set_foreground(l, "#CC99FF")
        self.view.set_background(self.win, "#001100")

    def run(self, parent):
        self.win.show_all()
        try:
            self.set_transient_for(None)
        except TypeError:
            print "Tested error for incorrect transient, it worked."
        print "All tests ok"

        self.set_transient_for(parent.win)
        self.set_transient_for(parent)

        gtk.mainloop()

f = FooController(FooView())
f.run()

