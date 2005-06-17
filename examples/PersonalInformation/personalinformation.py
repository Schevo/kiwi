# This example illustrates the use of entries with validations

import datetime

from Kiwi2 import Delegates, datatypes
from Kiwi2.initgtk import gtk, quit_if_last
from Kiwi2.Widgets import Entry

class Person:
    pass

class Form(Delegates.Delegate):

    def __init__(self):
        Delegates.Delegate.__init__(self, 
                                    gladefile="personalinformation",
                                    widgets=['name', 'age', 'birthdate',
                                             'height', 'weight', 'about', 
                                             'sex', 'nationality', 'ok_btn'],
                                    delete_handler=quit_if_last)
    
        self.nationality.prefill(['Brazilian', 'Yankee', 'Other'])
        self.sex.prefill(('Male', 'Female'))
        self.register_validate_function(self.validity)
        self.height.set_data_format('%4.4f')
        
    # here we define our custom validation. When a user types anything,
    # the validate signal calls methods with the signature 
    # on_widgetname__validate
    def on_name__validate(self, widget, data):
        if len(data) > 20:
            # we need to return an exception that will be displayed on
            # the information tooltip and the delegate option
            return datatypes.ValidationError("The name is too long")
    
    def on_height__validate(self, widget, data):
        if data > 200:
            return datatypes.ValidationError("The height is too tall")
        
    def on_weight__validate(self, widget, data):
        if float(data) > 90:
            # this is really not the type of validation that you would use :)
            # anyway, it's just for reference
            return datatypes.ValidationError("Dude! You need to lose some weight!")
    
    def validity(self, valid):
        print 'validity() called with value ', valid
        self.ok_btn.set_sensitive(valid)

person = Person()
person.name = 'John Doe'
person.age = 36
person.birthdate = datetime.datetime(year=1969, month=2, day=20)
person.height = 183.0
person.weight = 86.0
person.nationality = 'Yankee'
person.about = 'Kinda fat'

form = Form()
proxy = form.add_proxy(person, ['name', 'age', 'birthdate',
                                'height', 'weight', 'about',
                                'nationality'])
form.show_all()

def on_ok_btn_clicked(widget):
    print "Name:", person.name
    print "Age:", person.age
    print "Birthday:", person.birthdate
    print "Height:", person.height
    print "Weight:", person.weight
    print "Nationality:", person.nationality
    print "About Your self:", person.about
    
    gtk.main_quit()


form.ok_btn.connect("clicked", on_ok_btn_clicked)
gtk.main()
