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

from Kiwi2.initgtk import gtk, gobject
from Kiwi2.Widgets import WidgetProxy
from Kiwi2.utils import gsignal, gproperty
from Kiwi2 import ValueUnset

class SpinButton(gtk.SpinButton, WidgetProxy.MixInSupportMandatory):
    WidgetProxy.implementsIProxy()
    WidgetProxy.implementsIMandatoryProxy()

    # the value-changed signal is not emitted when you type a value
    # (instead of using the arrows) so we use the changed signal
    # inherited from gtk.Entry
    gsignal('changed', 'override')
    
    # mandatory widgets need to have this signal connected
    gsignal('expose-event', 'override')
    
    
    def __init__(self):
        # since the default data_type is str we need to set it to int or float for spinbuttons
        WidgetProxy.MixInSupportMandatory.__init__(self, data_type=int)
        gtk.SpinButton.__init__(self)
    
    def _check_entry(self):
        if len(self.get_text()) == 0 and self._mandatory:
            self._draw_mandatory_icon = True
        else:
            self._draw_mandatory_icon = False
    
    def set_data_type(self, data_type):
        old_datatype = self._data_type
        WidgetProxy.MixInSupportMandatory.set_data_type(self, data_type)
        if self._data_type not in (int, float):
            self._data_type = old_datatype
            raise TypeError("SpinButtons only accept integer or float values")
        
    def do_changed(self):
        self._check_entry()
        
        self.emit('content-changed')
        self.chain()

    def read(self):
        return self.get_value()

    def update(self, data):
        # first, trigger some basic validation
        WidgetProxy.MixInSupportMandatory.update(self, data)
        if data is not ValueUnset:
            self.set_value(data)
        else:
            self.set_value("")
    
    def do_expose_event(self, event):
        """Check WidgetProxy.MixInSupportMandatory.do_expose_event doc
        to know why this methos is been overriden.
        """
        result = self.chain(event)
        
        self.set_drawing_windows(self, self.window)
        
        if self._draw_mandatory_icon:
            self._draw_icon()
        return result
    
    
gobject.type_register(SpinButton)
