import datetime
import unittest

from kiwi.argcheck import argcheck, number, percent

class ArgTest(unittest.TestCase):
    def testOneArg(self):
        f = argcheck(str)(lambda s: None)
        f('str')
        self.assertRaises(TypeError, f, None)
        self.assertRaises(TypeError, f, 1)

    def testTwoArgs(self):
        f = argcheck(str, int)(lambda s, i: None)
        f('str', 1)
        self.assertRaises(TypeError, f, 1, 1)         # first incorret
        self.assertRaises(TypeError, f, 'str', 'str') # second incorrect
        self.assertRaises(TypeError, f, 1, 'str')     # swapped
        self.assertRaises(TypeError, f, 1)            # too few
        self.assertRaises(TypeError, f, 'str', 1, 1)  # too many

    def testVarArgs(self):
        f = argcheck(int)(lambda *v: None)
        f(1)
        f(1, 'str')
        f(1, 2, 3)
        #self.assertRaises(TypeError, f, 'str')

    def testDefault(self):
        f1 = lambda a, b=1: None
        d1 = argcheck(int, int)(f1)
        self.assertRaises(TypeError, d1, 'f')

        f2 = lambda a, b='str': None
        self.assertRaises(TypeError, argcheck, f2)

    def testKwargs(self):
        self.assertRaises(TypeError, argcheck, lambda **kw: None)

    def testUserDefined(self):
        class Payment(object):
            pass

        @argcheck(Payment, str)
        def pay(payment, description):
            pass
        pay(Payment(), 'foo')
        self.assertRaises(TypeError, 'bar', 'bar')
        self.assertRaises(TypeError, Payment(), Payment())

    def testClass(self):
        class Custom(object):
            pass

        class Test:
            @argcheck(int, int)
            def method1(self, foo, bar):
                return foo + bar

            @argcheck(Custom, int, datetime.datetime, int, int,
                      float, float)
            def method2(self, a, b, c, d, e, f, g=0.0):
                return g

            @argcheck(str, datetime.datetime, datetime.datetime)
            def method3(self, s, date=None, date2=None):
                return

            @argcheck(percent)
            def method4(self, n):
                return n

        t = Test()
        self.assertEqual(t.method1(1, 2), 3)
        self.assertRaises(TypeError, t.method1, None, None)
        self.assertEqual(t.method2(Custom(), 2, datetime.datetime.now(),
                                   4, 5, 6.0), 0.0)

        t.method3('foo')
        t.method3('bar', None)
        t.method3('baz', None, None)
        t.method3(s='foo')
        t.method3(s='bar', date=None)
        t.method3(s='baz', date=None, date2=None)
        t.method4(n=0)
        t.method4(n=50)
        t.method4(n=100)
        self.assertRaises(TypeError, t.method3, 'noggie', True)
        self.assertRaises(TypeError, t.method3, 'boogie', None, True)
        self.assertRaises(TypeError, t.method3, s='noggie', date2=True)
        self.assertRaises(TypeError, t.method3, s='boogie',
                          date=None, date2=True)
        self.assertRaises(ValueError, t.method4, -1)
        self.assertRaises(ValueError, t.method4, 101)

    def testNone(self):
        @argcheck(datetime.datetime)
        def func_none(date=None):
            return date
        func_none()
        func_none(None)
        self.assertRaises(TypeError, func_none, True)
        self.assertRaises(TypeError, func_none, date=True)

        @argcheck(str, datetime.datetime, datetime.datetime)
        def func_none2(s, date=None, date2=None):
            return date

        func_none2('foo')
        func_none2('bar', None)
        func_none2('baz', None, None)
        func_none2(s='foo')
        func_none2(s='bar', date=None)
        func_none2(s='baz', date=None, date2=None)
        self.assertRaises(TypeError, func_none2, 'noggie', True)
        self.assertRaises(TypeError, func_none2, 'boogie', None, True)
        self.assertRaises(TypeError, func_none2, s='noggie', date2=True)
        self.assertRaises(TypeError, func_none2, s='boogie',
                          date=None, date2=True)


    def testCustom(self):
        @argcheck(number)
        def func(n):
            pass
        func(10)

    def testDisable(self):
        argcheck.disable()
        @argcheck(str)
        def func(s):
            pass
        func(10)
        argcheck.enable()

    def testErrorHandling(self):
        self.assertRaises(TypeError, argcheck(str), True)
        self.assertRaises(TypeError, argcheck(int), lambda **x: None)
        self.assertRaises(TypeError, argcheck(int), lambda : None)
        self.assertRaises(TypeError, argcheck(int), lambda x='str': None)

if __name__ == '__main__':
    unittest.main()
