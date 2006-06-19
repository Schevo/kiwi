import cPickle
import datetime
import unittest
import locale

from kiwi.datatypes import currency, converter, ValidationError, ValueUnset, \
     Decimal

def set_locale(category, name):
    # set the date format to the spanish one
    try:
        locale.setlocale(category, name)
    except locale.Error:
        print 'skipping %s, locale not available' % name
        return False
    return True

class RegistryTest(unittest.TestCase):
    def testAdd(self):
        self.assertRaises(TypeError, converter.add, object)

class BoolTest(unittest.TestCase):
    def setUp(self):
        self.conv = converter.get_converter(bool)

    def testFromString(self):
        self.assertEqual(self.conv.from_string('TRUE'), True)
        self.assertEqual(self.conv.from_string('true'), True)
        self.assertEqual(self.conv.from_string('TrUe'), True)
        self.assertEqual(self.conv.from_string('1'), True)
        self.assertEqual(self.conv.from_string('FALSE'), False)
        self.assertEqual(self.conv.from_string('false'), False)
        self.assertEqual(self.conv.from_string('FalSE'), False)
        self.assertEqual(self.conv.from_string('0'), False)

        # you are not supposed to pass something that is not a string
        self.assertRaises(AttributeError, self.conv.from_string, None)

class DateTest(unittest.TestCase):
    def setUp(self):
        set_locale(locale.LC_TIME, 'C')
        self.date = datetime.date(1979, 2, 12)
        self.conv = converter.get_converter(datetime.date)

    def tearDown(self):
        set_locale(locale.LC_TIME, 'C')

    def testFromStringES(self):
        if not set_locale(locale.LC_TIME, 'es_ES'):
            return

        self.assertEqual(self.conv.from_string("12/2/79"), self.date)
        self.assertEqual(self.conv.from_string("12/02/79"), self.date)

    def testAsStringES(self):
        if not set_locale(locale.LC_TIME, 'es_ES'):
            return

        self.assertEqual(self.conv.as_string(self.date), "12/02/79")

    def testFromStringBR(self):
        if not set_locale(locale.LC_TIME, 'pt_BR'):
            return

        self.assertEqual(self.conv.from_string("12-2-1979"), self.date)
        self.assertEqual(self.conv.from_string("12-02-1979"), self.date)

        # test some invalid dates
        self.assertRaises(ValidationError,
                          self.conv.from_string, "40-10-2005")
        self.assertRaises(ValidationError,
                          self.conv.from_string, "30-02-2005")

    def testAsStringBR(self):
        if not set_locale(locale.LC_TIME, 'pt_BR'):
            return

        self.assertEqual(self.conv.as_string(self.date), "12-02-1979")

class CurrencyTest(unittest.TestCase):
    def setUp(self):
        set_locale(locale.LC_ALL, 'C')
        self.conv = converter.get_converter(currency)

    def tearDown(self):
        set_locale(locale.LC_ALL, 'C')

    def testFormatBR(self):
        if not set_locale(locale.LC_ALL, 'pt_BR'):
            return

        self.assertEqual(currency(100).format(), 'R$ 100')
        self.assertEqual(currency('123,45').format(), 'R$ 123,45')
        self.assertEqual(currency(12345).format(), 'R$ 12.345')
        self.assertEqual(currency(-100).format(), 'R$ -100')
        try:
            c = currency('R$1.234.567,40')
        except:
            raise AssertionError("monetary separator could not be removed")
        self.assertEqual(c, Decimal('1234567.40'))

        # Sometimes it works, sometimes it doesn''10,000,000.0't
        #self.assertEqual(self.conv.from_string('0,5'), currency('0.5'))

    def testFormatUS(self):
        if not set_locale(locale.LC_MONETARY, 'en_US'):
            return

        self.assertEqual(currency(100).format(), '$100')
        self.assertEqual(currency('123.45').format(), '$123.45')
        self.assertEqual(currency(12345).format(), '$12,345')
        self.assertEqual(currency(-100).format(), '$-100')
        self.assertEqual(currency(1).format(True), '$1')
        self.assertEqual(currency(1).format(False), '1')
        self.assertEqual(currency(0).format(True), '$0')

        self.assertEqual(self.conv.from_string(''), ValueUnset)
        self.assertEqual(self.conv.from_string('0'), currency(0))
        self.assertEqual(self.conv.from_string('0.5'), currency('0.5'))
        self.assertRaises(ValidationError, self.conv.from_string, 'foo')

        self.assertEqual(self.conv.as_string(currency(0)), '$0.00')
        self.assertEqual(self.conv.as_string(currency(-10)), '$-10.00')
        #self.assertEqual(ValidationError, self.conv.as_string, object)

    def testPickle(self):
        pickled_var = cPickle.dumps(currency("123.45"))
        recoverd_var = cPickle.loads(pickled_var)    
        self.assertEqual(recoverd_var.format(), '$123.45')
        
    def testPickleBR(self):
        if not set_locale(locale.LC_ALL, 'pt_BR'):
            return

        pickled_var = cPickle.dumps(currency("123.45"))
        recoverd_var = cPickle.loads(pickled_var)    
        self.assertEqual(recoverd_var.format(), 'R$ 123,45')
        
    def testPickleUS(self):
        if not set_locale(locale.LC_ALL, 'en_US'):
            return

        pickled_var = cPickle.dumps(currency("12123.45"))
        recoverd_var = cPickle.loads(pickled_var)    
        self.assertEqual(recoverd_var.format(), '$12,123.45')

class UnicodeTest(unittest.TestCase):
    def setUp(self):
        self.conv = converter.get_converter(unicode)

    def testFromString(self):
        self.assertEqual(self.conv.from_string('foobar'), u'foobar')
        # utf-8 encoded, as default after importing gtk
        self.assertEqual(self.conv.from_string('\xc3\xa4'), u'\xe4')

    def testAsString(self):
        self.assertEqual(self.conv.as_string(u'foobar'), 'foobar')
        self.assertEqual(self.conv.as_string(u'\xe4'), '\xc3\xa4')

class IntTest(unittest.TestCase):
    def setUp(self):
        self.conv = converter.get_converter(int)

    def tearDown(self):
        set_locale(locale.LC_ALL, 'C')

    def testFromString(self):
        self.assertEqual(self.conv.from_string('0'), 0)
        self.assertRaises(ValidationError, self.conv.from_string, '0.5')

    def testAsString(self):
        self.assertEqual(self.conv.as_string(0), '0')
        self.assertEqual(self.conv.as_string(-10), '-10')

    def testAsStringUS(self):
        if not set_locale(locale.LC_NUMERIC, 'en_US'):
            return

        self.assertEqual(self.conv.as_string(123456789), '123456789')

class FloatTest(unittest.TestCase):
    def setUp(self):
        self.conv = converter.get_converter(float)

    def tearDown(self):
        set_locale(locale.LC_ALL, 'C')

    def testFromString(self):
        self.assertEqual(self.conv.from_string('0'), 0.0)
        self.assertEqual(self.conv.from_string('-0'), 0.0)
        self.assertEqual(self.conv.from_string('0.'), 0.0)
        self.assertEqual(self.conv.from_string('0.0'), 0.0)
        self.assertEqual(self.conv.from_string('.5'), .5)
        self.assertEqual(self.conv.from_string('-2.5'), -2.5)
        self.assertEqual(self.conv.from_string('10.33'), 10.33)
        self.assertEqual(self.conv.from_string('0.00000000001'), 0.00000000001)
        self.assertRaises(ValidationError, self.conv.from_string, 'foo')
        self.assertRaises(ValidationError, self.conv.from_string, '1.2.3')
        self.assertEqual(self.conv.from_string(''), ValueUnset)

    def testFromStringUS(self):
        if not set_locale(locale.LC_NUMERIC, 'en_US'):
            return
        self.assertEqual(self.conv.from_string('0.'), 0)
        self.assertEqual(self.conv.from_string('1.75'), 1.75)
        self.assertEqual(self.conv.from_string('10,000'), 10000)
        self.assertEqual(self.conv.from_string('10,000,000.5'), 10000000.5)
        self.assertRaises(ValidationError,
                          self.conv.from_string, ',210,000,000.5')

    def testFromStringSE(self):
        # Swedish is interesting here because it has different
        # thousand separator and decimal points (compared to en_US)
        if not set_locale(locale.LC_NUMERIC, 'sv_SE'):
            return
        self.assertEqual(self.conv.from_string('0,'), 0)
        self.assertEqual(self.conv.from_string('1,75'), 1.75)
        self.assertEqual(self.conv.from_string('4 321'), 4321)
        self.assertEqual(self.conv.from_string('54 321'), 54321)
        self.assertEqual(self.conv.from_string('654 321'), 654321)
        self.assertEqual(self.conv.from_string('7 654 321'), 7654321)
        self.assertEqual(self.conv.from_string('10 000 000,5'), 10000000.5)
        self.assertRaises(ValidationError, self.conv.from_string, '1,2 3')
        self.assertRaises(ValidationError, self.conv.from_string, '1 23 ')
        self.assertRaises(ValidationError, self.conv.from_string, ' 23 ')
        #self.assertRaises(ValidationError, self.conv.from_string, '1234 234')

    def testAsString(self):
        self.assertEqual(self.conv.as_string(0.0), '0.0')
        self.assertEqual(self.conv.as_string(0.5), '0.5')
        self.assertEqual(self.conv.as_string(-0.5), '-0.5')
        self.assertEqual(self.conv.as_string(0.123456789), '0.123456789')
        self.assertEqual(self.conv.as_string(-0.123456789), '-0.123456789')
        self.assertEqual(self.conv.as_string(10000000), '10000000.0')
        self.assertEqual(self.conv.as_string(10000000.0), '10000000.0')

    def testAsStringUS(self):
        if not set_locale(locale.LC_NUMERIC, 'en_US'):
            return
        self.assertEqual(self.conv.as_string(10000000), '10,000,000.0')
        self.assertEqual(self.conv.as_string(10000000.0), '10,000,000.0')

    def testAsStringSE(self):
        if not set_locale(locale.LC_NUMERIC, 'sv_SE'):
            return
        self.assertEqual(self.conv.as_string(0.0), '0,0')
        self.assertEqual(self.conv.as_string(0.5), '0,5')
        self.assertEqual(self.conv.as_string(-0.5), '-0,5')
        self.assertEqual(self.conv.as_string(0.123456789), '0,123456789')
        self.assertEqual(self.conv.as_string(-0.123456789), '-0,123456789')
        self.assertEqual(self.conv.as_string(10000000), '10000000,0')
        self.assertEqual(self.conv.as_string(10000000.0), '10000000,0')


class DecimalTest(unittest.TestCase):
    def setUp(self):
        set_locale(locale.LC_NUMERIC, 'C')
        self.conv = converter.get_converter(Decimal)

    def tearDown(self):
        set_locale(locale.LC_NUMERIC, 'C')

    def testFromString(self):
        self.assertEqual(self.conv.from_string('-2.5'), Decimal('-2.5'))
        self.assertEqual(self.conv.from_string('10.33'), Decimal('10.33'))
        self.assertRaises(ValidationError, self.conv.from_string, 'foo')
        self.assertRaises(ValidationError, self.conv.from_string, '1.2.3')
        self.assertEqual(self.conv.from_string(''), ValueUnset)

    def testAsString(self):
        self.assertEqual(self.conv.as_string(Decimal('0.0')), '0.0')
        self.assertEqual(self.conv.as_string(Decimal('0.5')), '0.5')
        self.assertEqual(self.conv.as_string(Decimal('-0.5')), '-0.5')
        self.assertEqual(self.conv.as_string(Decimal('0.123456789')), '0.123456789')
        self.assertEqual(self.conv.as_string(Decimal('-0.123456789')), '-0.123456789')
        self.assertEqual(self.conv.as_string(Decimal('10000000')), '10000000.0')
        self.assertEqual(self.conv.as_string(Decimal('10000000.0')), '10000000.0')

    def testAsStringUS(self):
        if not set_locale(locale.LC_NUMERIC, 'en_US'):
            return
        self.assertEqual(self.conv.as_string(Decimal('10000000')), '10,000,000.0')
        self.assertEqual(self.conv.as_string(Decimal('10000000.0')), '10,000,000.0')

    def testAsStringSE(self):
        if not set_locale(locale.LC_NUMERIC, 'sv_SE'):
            return
        self.assertEqual(self.conv.as_string(Decimal('0.0')), '0,0')
        self.assertEqual(self.conv.as_string(Decimal('0.5')), '0,5')
        self.assertEqual(self.conv.as_string(Decimal('-0.5')), '-0,5')
        self.assertEqual(self.conv.as_string(Decimal('0.123456789')), '0,123456789')
        self.assertEqual(self.conv.as_string(Decimal('-0.123456789')), '-0,123456789')
        self.assertEqual(self.conv.as_string(Decimal('10000000')), '10000000,0')
        self.assertEqual(self.conv.as_string(Decimal('10000000.0')), '10000000,0')

if __name__ == "__main__":
    unittest.main()
