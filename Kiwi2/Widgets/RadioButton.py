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

"""Defines an enhanced version of GtkRadioButton"""

from Kiwi2 import ValueUnset
from Kiwi2.initgtk import gtk, gobject
from Kiwi2.Widgets import WidgetProxy
from Kiwi2.utils import gsignal, gproperty

class RadioButton(gtk.RadioButton, WidgetProxy.Mixin):
    WidgetProxy.implementsIProxy()
    gsignal('toggled', 'override')
    gproperty('data-value', str, nick='Data Value')

    def __init__(self):
        WidgetProxy.Mixin.__init__(self)
        gtk.RadioButton.__init__(self)
        self._data_value = None
    
    def do_toggled(self):
        self.emit('content-changed')
        self.chain()

    def read(self):
        for rb in self.get_group():
            if rb.get_active():
                return self.str2type(rb.get_data_value())

    def update(self, data):
        # first, trigger some basic validation
        WidgetProxy.Mixin.update(self, data)
        if data is None or data is ValueUnset:
            return
        data = self.type2str(data)
        for rb in self.get_group():
            if rb.get_data_value() == data:
                rb.set_active(True)
    
    def set_data_value(self, data):
        self._data_value = data
    
    def get_data_value(self):
        return self._data_value

gobject.type_register(RadioButton)
