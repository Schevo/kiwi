#!/usr/bin/env python
from Kiwi import Views, mainquit

widgets = [ "the_label" ]
app = Views.GladeView(gladefile="hey", 
                      delete_handler=mainquit, 
                      widgets=widgets)

print app.the_label         # the_label, a widget defined in glade, is 
app.the_label.set_bold()    # now an instance variable of the view
app.show_and_loop()

