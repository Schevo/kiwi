#!/usr/bin/env python

from utils import refresh_gui

from Kiwi2.Widgets.List import List, Column
from Kiwi2.initgtk import gtk, quit_if_last

from unittest import TestCase, TestSuite, makeSuite, TextTestRunner
import sys

# this is the delay between each refresh of the screen in seconds
delay = 0

class ListTest(TestCase):

    def setUp(self):
        self.win = gtk.Window()
        self.win.set_default_size(400, 400)

    def tearDown(self):
        self.win.destroy()
        del self.win

    def testEmptyList(self):
        global delay
        mylist = List()
        self.win.add(mylist)
        self.win.show_all()
        refresh_gui(delay)

    def testOneColumn(self):
        global delay
        # column's attribute can not contain spaces
        self.assertRaises(AttributeError, Column, 'test column')
        
        mylist = List(Column('test_column'))
        self.win.add(mylist)
        self.win.show_all()
        refresh_gui(delay)

        self.assertEqual(1, len(mylist.treeview.get_columns()))
        

    def testAddingOneInstance(self):
        global delay

        mylist = List([Column('name'), Column('age')])
        self.win.add(mylist)
        self.win.show_all()
        refresh_gui(delay)

        class Person:
            def __init__(self, name, age):
                self.name, self.age = name, age
                
        person = Person('henrique', 21)
        mylist.add_instance(person)

        refresh_gui(delay)

        # usually you don't use the model directly, but tests are all about
        # breaking APIs, right?
        self.assertEqual(mylist.model[0][0], person)
        self.assertEqual(mylist.model[0][0].name, 'henrique')
        self.assertEqual(mylist.model[0][0].age, 21)
    
if __name__ == '__main__':
    import sys
    if len(sys.argv) == 2:
        delay = float(sys.argv[1])
    suite = TestSuite()
    suite.addTest(makeSuite(ListTest))
    TextTestRunner(verbosity=2).run(suite)
    
