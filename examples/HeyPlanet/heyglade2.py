#!/usr/bin/env python
from Kiwi2 import Views
from Kiwi2.initgtk import gtk, quit_if_last

widgets = ["the_label"]
app = Views.BaseView(gladefile="hey", 
                     delete_handler=quit_if_last, 
                     widgets=widgets)

# the_label, a widget defined in glade, is 
text = app.the_label.get_text()
# now an instance variable of the view
app.the_label.set_markup('<b>%s</b>' % text)
app.the_label.set_use_markup(True)
app.show()
gtk.main()
