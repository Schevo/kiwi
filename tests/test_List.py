#!/usr/bin/env python

from utils import refresh_gui

from Kiwi2.Widgets.List import List, Column
from Kiwi2.initgtk import gtk, quit_if_last

from unittest import TestCase, TestSuite, makeSuite, TextTestRunner
import sys

class Person:
    def __init__(self, name, age):
        self.name, self.age = name, age        

# we will use this tuple in several tests
persons = (Person('Johan', 24), Person('Gustavo', 25),
           Person('Kiko', 28), Person('Salgado', 25),
           Person('Lorenzo', 26), Person('Henrique', 21))

# this is the delay between each refresh of the screen in seconds
delay = 0

class ColumnTests(TestCase):

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
        

class DataTests(TestCase):
    """In all this tests we use the same configuration for a list"""
    def setUp(self):
        self.win = gtk.Window()
        self.win.set_default_size(400, 400)
        self.list = List([Column('name'), Column('age')])
        self.win.add(self.list)
        self.win.show_all()
        refresh_gui(delay)

    def tearDown(self):
        self.win.destroy()
        del self.win

    def testAddingOneInstance(self):
        global delay

        # we should have two columns now
        self.assertEqual(2, len(self.list.treeview.get_columns()))
                         
        person = Person('henrique', 21)
        self.list.add_instance(person)

        refresh_gui(delay)

        # usually you don't use the model directly, but tests are all about
        # breaking APIs, right?
        self.assertEqual(self.list.model[0][0], person)
        self.assertEqual(self.list.model[0][0].name, 'henrique')
        self.assertEqual(self.list.model[0][0].age, 21)

        # we still have to columns, right?
        self.assertEqual(2, len(self.list.treeview.get_columns()))

    def testAddingAList(self):
        global delay, persons

        self.list.add_list(persons)
        refresh_gui(delay)
        
        self.assertEqual(len(self.list), len(persons))
        
    def testAddingABunchOfInstances(self):
        global delay, persons

        for person in persons:
            self.list.add_instance(person)
            refresh_gui(delay)

        self.assertEqual(len(self.list), len(persons))

    def testRemovingOneInstance(self):
        global delay, persons

        self.list.add_list(persons)
        refresh_gui(delay)

        # we are going to remove Kiko
        person = persons[2]

        self.list.remove_instance(person)

        self.assertEqual(len(self.list), len(persons) - 1)

        # now let's remove something that is not on the list
        new_person = Person('Evandro', 24)
        self.assertRaises(ValueError, self.list.remove_instance, new_person)

        # note that even a new person with the same values as a person
        # in the list is not considered to be in the list
        existing_person = Person('Gustavo', 25)
        self.assertRaises(ValueError, self.list.remove_instance,
                          existing_person)
        
        
if __name__ == '__main__':
    import sys
    if len(sys.argv) == 2:
        delay = float(sys.argv[1])
    suite = TestSuite()
    suite.addTest(makeSuite(ColumnTests))
    suite.addTest(makeSuite(DataTests))
    TextTestRunner(verbosity=2).run(suite)
    
