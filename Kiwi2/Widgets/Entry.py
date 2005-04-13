#!/usr/bin/env python
#
# Kiwi: a Framework and Enhanced Widgets for Python
#
# Copyright (C) 2003-2004 Async Open Source
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
# 
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307
# USA
# 
# Author(s): Christian Reis <kiko@async.com.br>
#

import time

from Kiwi2 import ValueUnset
from Kiwi2.initgtk import gtk, gobject
from Kiwi2.Widgets import WidgetProxy
from Kiwi2.Widgets.datatypes import ValidationError
from Kiwi2.utils import gsignal, gproperty


class Entry(gtk.Entry, WidgetProxy.MixinSupportValidation):
    """The Kiwi Entry widget has many special features that extend the basic gtk entry.
    
    First of all, as every Kiwi Widget, it implements the Proxy protocol. As the users 
    types the entry can interact with the application model automaticly. 
    Kiwi Entry also implements intresting UI additions. If the input data does not match
    the data type of the entry the background nicely fades to a light red color. 
    As the background changes an information icon appears. When the user
    passes the mouse over the infomation icon a tooltip is displayed informing the
    user how to correctly fill the entry. When dealing with date and float data-type
    the information on how to fill these entries is displayed according to the 
    current locale.
    """
    WidgetProxy.implementsIProxy()
    WidgetProxy.implementsIMandatoryProxy()
    
    gsignal('changed', 'override')
    # mandatory widgets need to have this signal connected
    gsignal('expose-event', 'override')
    
    def __init__(self):
        gtk.Entry.__init__(self)
        WidgetProxy.MixinSupportValidation.__init__(self)
        self.connect("expose-event", self._set_icon_draw_info)
        
    def _set_icon_draw_info(self, widget, event):
        self._widget = self
        self._gdk_window = self.window
    
    def do_changed(self):
        """Called when the content of the entry changes.

        Sets an internal variable that stores the last time the user
        changed the entry
        """
        
        self._last_change_time = time.time()
        
        if len(self.get_text()) == 0 and self._mandatory:
            self._draw_mandatory_icon = True
        else:
            self._draw_mandatory_icon = False
        
        self.emit('content-changed')
        self.chain()
        
    def read(self):
        """Called after each caracter is typed. If the input is wrong start 
        complaining
        """
        text = self.get_text()
        data = self._validate_data(text)
        
        return data

    def update(self, data):
        WidgetProxy.MixinSupportValidation.update(self, data)

        if data is ValueUnset or data is None:
            self.set_text("")
        else:
            self.set_text(self.type2str(data))

    def set_text(self, text):
        gtk.Entry.set_text(self, text)
        self.emit('content-changed')
        
    def do_expose_event(self, event):
        """Expose-event signal are triggered when a redraw of the widget
        needs to be done.
        
        Draws information and mandatory icons when necessary
        """        
        result = self.chain(event)
        
        # set this attributes so the draw icon method knows where to draw
        self._widget = self
        self._gdk_window = self.window
        
        self._define_icons_to_draw()
        
        return result
              
gobject.type_register(Entry)
    
