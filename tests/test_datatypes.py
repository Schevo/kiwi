import unittest
import locale

from datetime import date
from Kiwi2.Widgets import datatypes

class DataTypesTest(unittest.TestCase):

    def teststr2bool(self):
        self.assertEqual(datatypes.str2bool('TRUE'), True)
        self.assertEqual(datatypes.str2bool('true'), True)
        self.assertEqual(datatypes.str2bool('TrUe'), True)
        self.assertEqual(datatypes.str2bool('1'), True)
        self.assertEqual(datatypes.str2bool('FALSE'), False)
        self.assertEqual(datatypes.str2bool('false'), False)
        self.assertEqual(datatypes.str2bool('FalSE'), False)
        self.assertEqual(datatypes.str2bool('0'), False)

        # testing with default values
        self.assertEqual(datatypes.str2bool('something', False), False)
        self.assertEqual(datatypes.str2bool('something', True), True)
        self.assertEqual(datatypes.str2bool('', True), True)
        self.assertEqual(datatypes.str2bool('', False), False)

        # you are not supposed to pass something that is not a string
        self.assertRaises(AttributeError, datatypes.str2bool, None)

    def teststr2date(self):
        # set the date format to the spanish one
        locale.setlocale(locale.LC_TIME, 'es_ES')
        date_format = locale.nl_langinfo(locale.D_FMT)
        datatypes.set_date_format(date_format)

        birthdate = date(1979, 2, 12)
        # in the spanish locale the format of a date is %d/%m/%y
        self.assertEqual(datatypes.str2date("12/2/79"), birthdate)
        self.assertEqual(datatypes.str2date("12/02/79"), birthdate)

        # let's try with the portuguese locale
        locale.setlocale(locale.LC_TIME, 'pt_BR')
        date_format = locale.nl_langinfo(locale.D_FMT)
        datatypes.set_date_format(date_format)

        # portuguese format is "%d-%m-%Y"
        self.assertEqual(datatypes.str2date("12-2-1979"), birthdate)
        self.assertEqual(datatypes.str2date("12-02-1979"), birthdate)

        # test some invalid dates
        self.assertRaises(ValueError, datatypes.str2date, "40-10-2005")
        # february only have 28 days
        self.assertRaises(ValueError, datatypes.str2date, "30-02-2005")
        
    def testdate2str(self):
        locale.setlocale(locale.LC_TIME, 'es_ES')
        date_format = locale.nl_langinfo(locale.D_FMT)
        datatypes.set_date_format(date_format)

        birthdate = date(1979, 2, 12)

        self.assertEqual(datatypes.date2str(birthdate), "12/02/79")

        locale.setlocale(locale.LC_TIME, 'pt_BR')
        date_format = locale.nl_langinfo(locale.D_FMT)
        datatypes.set_date_format(date_format)

        self.assertEqual(datatypes.date2str(birthdate), "12-02-1979")

if __name__ == "__main__":
    unittest.main()
