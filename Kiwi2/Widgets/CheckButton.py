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
from Kiwi2.Widgets.WidgetProxy import WidgetProxyMixin, implementsIProxy
from Kiwi2.utils import gsignal

class CheckButton(gtk.CheckButton, WidgetProxyMixin):
    implementsIProxy()
    gsignal('toggled', 'override')
        
    def __init__(self):
        WidgetProxyMixin.__init__(self)
        gtk.CheckButton.__init__(self)
        self.set_property("data-type", "bool")
    
    def set_data_type(self, data_type):
        if data_type == "bool" or data_type is None:
            WidgetProxyMixin.set_data_type(self, data_type)
        else:
            raise TypeError, "CheckButtons only accept boolean values"

    def do_toggled(self):
        self.emit('content-changed')
        self.chain()
        
    def read(self):
        return self.get_active()

    def update(self, data):
        # first, trigger some basic validation
        WidgetProxyMixin.update(self, data)
        self.set_active(data)

gobject.type_register(CheckButton)
