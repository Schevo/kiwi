#!/usr/bin/env python
import sys
sys.path.insert(0, "..")
from Kiwi.Views import BaseView
from Kiwi.Controllers import BaseController
from Kiwi.initgtk import gtk
from gtk import keysyms

class FooX(BaseView, BaseController):
    widgets = [ "vbox", "label" ]
    def __init__(self):
        self.build_ui()
        BaseView.__init__(self, delete_handler=gtk.mainquit)
        BaseController.__init__(self, view=self)

    def build_ui(self):
        self.win = gtk.Window()
        vbox = gtk.VBox()
        self.label = gtk.Label("Pick one noogie")
        self.button = gtk.Button(label="Noogie!")
        vbox.add(self.button)
        self.foo__button = gtk.Button(label="Boogie!")
        vbox.add(self.foo__button)
        self.win.add(vbox)
        return vbox

    def on_button__clicked(self, *args):
        Bar().run(self)
        gtk.mainloop()

    def on_foo__button__clicked(self, *args):
        # This is subclassed
        raise AssertionError

    def run(self):
        self.win.show_all()
        gtk.mainloop()

class FooNotWidget(FooX):
    def __init__(self):
        self.vbox = self.build_ui()
        # It's dumb, and it breaks
        self.noogie = FooX
        BaseView.__init__(self, delete_handler=gtk.mainquit)
        BaseController.__init__(self, view=self)

    def on_noogie__haxored(self, *args):
        print "I AM NOT A NUMBER I AM A FREE MAN"

class Foo(FooX):
    def __init__(self):
        self.vbox = self.build_ui()
        BaseView.__init__(self, delete_handler=gtk.mainquit)
        BaseController.__init__(self, view=self)
        self.view.set_background(self.button, "#FF0099")
        self.view.set_background(self.foo__button, "#EEEE00")
        self.view.set_foreground(self.label, "#00FFEE")

    def A_pressed(*args):
        print "A was pressed", args
    
    def B_pressed(*args):
        print "B was pressed", args

    def on_foo__button__clicked(self, *args):
        print "FOO CORRECT"

    keyactions = {
        keysyms.A : A_pressed,
        keysyms.a : A_pressed,
        keysyms.B : B_pressed,
        keysyms.b : B_pressed,
    }

class FooY(FooX):
    def __init__(self):
        self.vbox = self.build_ui()
        self.win = gtk.FileSelection()
        BaseView.__init__(self, delete_handler=gtk.mainquit)
        BaseController.__init__(self, view=self)

class FooZ(FooX):
    def __init__(self):
        self.win = 0
        BaseView.__init__(self, delete_handler=gtk.mainquit)
        BaseController.__init__(self, view=self)

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
        self.set_transient_for(parent.win)
        self.set_transient_for(parent)
        try:
            self.set_transient_for(None)
        except TypeError:
            print "Tested error for incorrect transient, it worked."
        print "All tests ok"

f = Foo()
f.run()

try:
    f = FooX()
    raise AssertionError
except KeyError, e:
    print "error check #1 ok:", e

try:
    f = FooNotWidget()
    raise AssertionError
except AttributeError, e:
    print "error check #2 ok:", e

f = FooY()

try:
    f = FooZ()
    raise AssertionError
except TypeError, e:
    print "error check #3 ok:", e

