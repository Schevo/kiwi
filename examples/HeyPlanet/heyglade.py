#!/usr/bin/env python
from Kiwi2 import Views, gtk

app = Views.GladeView(gladefile="hey", delete_handler=gtk.main_quit)
app.show_and_loop()

