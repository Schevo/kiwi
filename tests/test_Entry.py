#!/usr/bin/env python
from utils import refresh_gui

from Kiwi2.Widgets import Entry

import unittest
import datetime
import time
import locale

class EntryTest(unittest.TestCase):
    def testValidDataType(self):
        
        locale_dictionary = locale.localeconv()
        
        entry = Entry()
        entry.set_property("data-type", "date")
        # let's make the entry complain!
        entry.set_text("string")
        self.assertEqual(entry.read(), None)
        self.assertNotEqual(entry._complain_checker_id, -1)
        #print entry._complain_checker_id
        
        # now let's put proper data
        entry.set_text("10/05/1952")
        self.assertEqual(entry.read(), datetime.date(1952, 10, 5))
        self.assertEqual(entry._background_timeout_id, -1)
        
        # now change the data-type and do it again
        entry.set_property("data-type", "float")
        if locale_dictionary["thousands_sep"] == ',':
            # correct value
            entry.set_text("23,400.2")
            self.assertEqual(entry.read(), 23400.2)
            self.assertEqual(entry._background_timeout_id, -1) 
            
            # wrong value
            entry.set_text("23.400,2")
            self.assertEqual(entry.read(), None)
        
        
if __name__ == '__main__':
    unittest.main()

