#!/usr/bin/env python
from utils import refresh_gui

from Kiwi2 import Delegates
from Kiwi2.initgtk import gtk, quit_if_last

from unittest import TestCase, TestSuite, makeSuite, TextTestRunner
import sys

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
        Delegates.Delegate.__init__(self, toplevel=self.win,
                                    delete_handler=quit_if_last)

    def on_foo__clicked(self, *args):
        self.x = "FOO in Foo"
    
    def on_bar__clicked(self, *args):
        self.y = "BAR in B"

class ClickCounter(Delegates.Delegate):
    """In this delegate we count the number of clicks we do"""
    def __init__(self):
        self.win = gtk.Window()
        self.button = gtk.Button('Click me!')
        self.win.add(self.button)
        Delegates.Delegate.__init__(self, toplevel=self.win,
                                    delete_handler=quit_if_last)

        self.clicks = 0

    def on_button__clicked(self, *args):
        self.clicks += 1

# this is the delay between each refresh of the screen in seconds
delay = 0

class DelegateTest(TestCase):
    def testButtons(self):
        global delay
        f = Foo()
        f.show_all()
        refresh_gui(delay)
        f.foo.clicked()
        refresh_gui(delay)
        self.assertEqual(f.x, "FOO in Foo")
        f.bar.clicked()
        refresh_gui(delay)
        self.assertEqual(f.y, "BAR in B")

    def testClickCounter(self):
        global delay
        clickcounter = ClickCounter()
        clickcounter.show_all()
        refresh_gui(delay)
        
        # one for the boys
        clickcounter.button.clicked()
        self.assertEqual(clickcounter.clicks, 1)

        # one for the girls
        clickcounter.button.clicked()
        self.assertEqual(clickcounter.clicks, 2)
        
if __name__ == '__main__':
    import sys
    if len(sys.argv) == 2:
        delay = float(sys.argv[1])
    suite = TestSuite()
    suite.addTest(makeSuite(DelegateTest))
    TextTestRunner(verbosity=2).run(suite)
    
