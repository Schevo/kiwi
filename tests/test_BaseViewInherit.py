#!/usr/bin/env python
import sys
sys.path.insert(0, "..")

from Kiwi import Delegates
from Kiwi.initgtk import gtk

class A:
    def on_foo__clicked(self, *args):
        self.x = "FOO in A"

class B:
    def on_foo__clicked(self, *args):
        self.x = "FOO in B"
    
    def on_bar__clicked(self, *args):
        self.y = "BAR in B"

class C:
    def on_foo__clicked(self, *args):
        self.x = "FOO in C"

class X(A,B,C):
    def on_foo__clicked(self, *args):
        self.x = "FOO in X"

class Y:
    def on_foo__clicked(self, *args):
        self.x = "FOO in Y"

class Foo(X,Y,Delegates.Delegate):
    widget  = ["foo"]
    def __init__(self):
        self.win = gtk.Window()
        self.foo = gtk.Button("CLICK ME AND BE HAPPY")
        self.bar = gtk.Button("CLICK ME AND BE HAPPY")
        v = gtk.VBox()
        v.add(self.foo)
        v.add(self.bar)
        self.win.add(v)
        self.x = self.y = "NOOO"
        Delegates.Delegate.__init__(self, delete_handler=gtk.mainquit)

    def on_foo__clicked(self, *args):
        self.x = "FOO in Foo"
        print "Foo clicked ok!"
    
    def on_bar__clicked(self, *args):
        self.y = "BAR in B"
        print "Bar clicked ok!"

f = Foo()
f.foo.clicked()
f.bar.clicked()
assert f.x == "FOO in Foo", f.x
assert f.y == "BAR in B", f.y
f.show_all_and_loop()
print "ok"
