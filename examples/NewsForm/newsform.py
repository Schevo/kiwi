#!/usr/bin/env python
from Kiwi2 import Views
from Kiwi2.initgtk import gtk, quit_if_last

# Empty model; GladeProxy will use it to hold the attributes
class NewsItem:
    """An instance representing an item of news. 
       Attributes: title, author, url"""
    pass

item = NewsItem()
my_widgets = ["title", "author", "url"]
view = Views.BaseView(gladefile="newsform", widgets=my_widgets,
                      delete_handler=quit_if_last)
view.add_proxy(item, my_widgets)
view.focus_topmost()
view.show()
gtk.main() # runs till window is closed as per delete_handler

print 'Item: "%s" (%s) %s' % (item.title, item.author, item.url)
