#!/usr/bin/env python
from utils import refresh_gui

from Kiwi2 import Delegates
from Kiwi2.initgtk import gtk, quit_if_last

from unittest import TestCase, TestSuite, makeSuite, TextTestRunner
import sys

class ActionDelegate(Delegates.Delegate):
    def __init__(self):
        Delegates.Delegate.__init__(self, gladefile="actions.glade",
                                    toplevel_name='window1',
                                    widgets=['New'],
                                    delete_handler=quit_if_last)
        self.new_activated = False

    def on_New__activate(self, *args):
        self.new_activated = True
        
# this is the delay between each refresh of the screen in seconds
delay = 0

class ActionTest(TestCase):
    def testButtons(self):
        global delay
        action_delegate = ActionDelegate()
        action_delegate.show_all()
        refresh_gui(delay)
        action_delegate.New.activate()
        refresh_gui(delay)
        self.assertEqual(action_delegate.new_activated, True)

if __name__ == '__main__':
    import sys
    if len(sys.argv) == 2:
        delay = float(sys.argv[1])
    suite = TestSuite()
    suite.addTest(makeSuite(ActionTest))
    TextTestRunner(verbosity=2).run(suite)
    
