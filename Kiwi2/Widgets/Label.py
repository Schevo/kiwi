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
from Kiwi2.utils import gsignal, gproperty, set_foreground

class Label(gtk.Label, WidgetProxyMixin):
    implementsIProxy()
    
    def __init__(self):
        gtk.Label.__init__(self)
        WidgetProxyMixin.__init__(self)
        self.set_use_markup(True)

    def read(self):
        return self.str2type(self.get_text())

    def update(self, data):
        # first, trigger some basic validation
        WidgetProxyMixin.update(self, data)
        
        self.set_text(self.type2str(data))

    def set_bold(self, value):
        if value:
            self.set_markup("<b>%s</b>" % self.get_text())
        else:
            self.set_markup(self.get_text())

    def set_color(self, color):
       set_foreground(self, color) 

gobject.type_register(Label)
