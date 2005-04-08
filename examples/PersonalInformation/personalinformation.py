# This example illustrates the use of entries with validations


from Kiwi2 import Views
from Kiwi2.initgtk import gtk, quit_if_last
from Kiwi2.Widgets import Entry

class Person:
    pass

class Form(Views.BaseView):

    def __init__(self):
        Views.BaseView.__init__(self, gladefile="personalinformation",
                                widgets=['name', 'age', 'birthdate', 'height'],
                                delete_handler=quit_if_last)

person = Person()
form = Form()
proxy = form.add_proxy(person, ['name', 'age', 'birthdate', 'height'])
form.show_all()
gtk.main()

print person.name, person.age, person.birthdate, person.height
