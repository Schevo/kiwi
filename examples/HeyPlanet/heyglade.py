#!/usr/bin/env python
from Kiwi2 import Views
from Kiwi2.initgtk import gtk, quit_if_last

app = Views.BaseView(gladefile="hey", delete_handler=quit_if_last)
app.show()
gtk.main()
