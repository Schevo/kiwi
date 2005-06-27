#!/usr/bin/env python

from utils import refresh_gui

from kiwi.Views import BaseView
from kiwi.Controllers import BaseController
from kiwi.initgtk import gtk
from kiwi import utils
from gtk import keysyms

import unittest

class FooView(BaseView):
    widgets = [ "vbox", "label" ]
    def __init__(self):
        self.build_ui()
        BaseView.__init__(self, toplevel_name='win')

    def build_ui(self):
        self.win = gtk.Window()
        vbox = gtk.VBox()
        self.label = gtk.Label("Pick one noogie")
        vbox.add(self.label)
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
        self.bar = Bar()

    def on_foo__button__clicked(self, *args):
        # This is subclassed
        self.view.label.set_text("Good click!")

    def run(self):
        self.view.show_all()

class Bar(BaseView, BaseController):
    def __init__(self):
        self.win = gtk.Window()
        self.label = gtk.Label("foobar!")
        self.win.add(self.label)
        BaseView.__init__(self, toplevel=self.win)
        BaseController.__init__(self, view=self)
        utils.set_foreground(self.label, "#CC99FF")
        utils.set_background(self.win, "#001100")

    def run(self, parent):
        self.show_all(parent)

# these classes are bad and should trigger exceptions

class NoWinFoo(BaseView, BaseController):
    def __init__(self):
        self.win = 0
        BaseView.__init__(self)
        BaseController.__init__(self, view=self)


class NotWidgetFoo(FooView, BaseController):
    def __init__(self):
        self.vbox = self.build_ui()
        # It's dumb, and it breaks
        self.noogie = NotWidgetFoo
        FooView.__init__(self)
        BaseController.__init__(self, view=self)

    def on_noogie__haxored(self, *args):
        print "I AM NOT A NUMBER I AM A FREE MAN"

class BaseViewTest(unittest.TestCase):

    def setUp(self):
        self.foo = FooController(FooView())
        self.foo.run()
        refresh_gui()

    def tearDown(self):
        for win in gtk.window_list_toplevels():
            win.destroy()

    def testFooButton(self):
        self.foo.view.foo__button.clicked()
        refresh_gui()
        self.assertEqual(self.foo.view.label.get_text(),
                         "Good click!")
        
    def testSubView(self):
        self.foo.view.button.clicked()
        self.foo.bar.run(self.foo.view)
        refresh_gui()
        self.assertEqual(self.foo.bar, self.foo.bar.view)
        self.assertEqual(self.foo.bar.toplevel, self.foo.bar.win)
        # setting None as transient window should be an error
        self.assertRaises(TypeError, self.foo.bar.set_transient_for, None)
    
    def testColors(self):
        self.foo.view.button.clicked()
        self.foo.bar.run(self.foo.view)
        refresh_gui()
        color = utils.get_background(self.foo.bar.win)
        self.assertEqual(color, "#001100")
        color = utils.get_foreground(self.foo.bar.label)
        self.assertEqual(color, "#CC99FF")


class BrokenViewsTest(unittest.TestCase):
    
    def testNoWindow(self):
        # A View requires an instance variable called toplevel that
        # specifies the toplevel widget in it
        self.assertRaises(TypeError, NoWinFoo)

    def testNotAWidget(self):
        # noogie (__main__.NotWidgetFoo) is not a widget and 
        # can't be connected to
        self.assertRaises(AttributeError, NotWidgetFoo)
        
if __name__ == '__main__':
    unittest.main()
