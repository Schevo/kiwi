#!/usr/bin/env python
import unittest

from Kiwi2 import Delegates
from Kiwi2.initgtk import quit_if_last
from utils import refresh_gui

class ActionDelegate(Delegates.Delegate):
    def __init__(self):
        Delegates.Delegate.__init__(self, gladefile="actions.glade",
                                    toplevel_name='window1',
                                    widgets=['New'],
                                    delete_handler=quit_if_last)
        self.new_activated = False

    def on_New__activate(self, *args):
        self.new_activated = True
        
class ActionTest(unittest.TestCase):
    def testButtons(self):
        action_delegate = ActionDelegate()
        action_delegate.show_all()
        refresh_gui()
        action_delegate.New.activate()
        refresh_gui()
        self.assertEqual(action_delegate.new_activated, True)

if __name__ == '__main__':
    unittest.main()
