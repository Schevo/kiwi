#!/usr/bin/env python
from utils import refresh_gui

from Kiwi2.Widgets import CheckButton

from unittest import TestCase, TestSuite, makeSuite, TextTestRunner
import sys

class CheckButtonTest(TestCase):
    def testForBool(self):
        myChkBtn = CheckButton()
        self.assertEqual(myChkBtn.get_property("data-type"), "bool")

        self.assertRaises(TypeError, myChkBtn.set_property, ('data-type',
        'bool'))

if __name__ == '__main__':
    import sys
    if len(sys.argv) == 2:
        delay = float(sys.argv[1])
    suite = TestSuite()
    suite.addTest(makeSuite(CheckButtonTest))
    TextTestRunner(verbosity=2).run(suite)
    
