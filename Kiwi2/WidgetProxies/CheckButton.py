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

from Kiwi.WidgetProxies.Base import WidgetProxy

class CheckButtonProxy(WidgetProxy):
    def __init__(self, proxy, widget, attr):
        WidgetProxy.__init__(self, proxy, widget, attr)
        self._connect("toggled", self.callback)

    def update(self, value):
        if value is None:
            value = False
        if value not in (True, False):
            msg = "bad value %s for widget %s:\nexpected integer/boolean"
            raise TypeError(msg % (repr(value), self.name))
        self._block_handlers()
        # set_active does *not* emit any signal, which is why we need to
        # call toggled() right after it.
        self.widget.set_active(value)
        self.widget.toggled()
        self._unblock_handlers()
        return value

    def read(self):
        return self.widget.get_active()

# They are the same thing, in reality (!)
ToggleButtonProxy = CheckButtonProxy

