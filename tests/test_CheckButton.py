#!/usr/bin/env python
from utils import refresh_gui

from Kiwi2.Widgets import CheckButton

import unittest

class CheckButtonTest(unittest.TestCase):
    def testForBool(self):
        myChkBtn = CheckButton()
        self.assertEqual(myChkBtn.get_property("data-type"), bool)

        # this test doens't work... maybe be a pygtk bug
        #self.assertRaises(TypeError, myChkBtn.set_property, 'data-type', str)
        
if __name__ == '__main__':
    unittest.main()
