#!/usr/bin/env python
from kiwi import Views
from kiwi.initgtk import gtk, quit_if_last

app = Views.BaseView(gladefile="hey", delete_handler=quit_if_last)
app.show()
gtk.main()
