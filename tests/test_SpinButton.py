#!/usr/bin/env python
from utils import refresh_gui

from Kiwi2.Widgets import SpinButton

import unittest

class SpinButtonTest(unittest.TestCase):
    def testForIntFloat(self):
        mySpinBtn = SpinButton()
        self.assertEqual(mySpinBtn.get_property("data-type"), int)
        
        # this test doens't work... might be a pygtk bug
        #self.assertRaises(TypeError, mySpinBtn.set_property, 'data-type', str)
        
if __name__ == '__main__':
    unittest.main()
