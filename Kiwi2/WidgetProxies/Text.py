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

from Kiwi.initgtk import gtk
from Kiwi.WidgetProxies.Base import EditableProxy

class TextProxy(EditableProxy):
    def __init__(self, proxy, widget, attr):
        EditableProxy.__init__(self, proxy, widget, attr)
        self._connect("changed", self.callback)

    def update(self, value):
        text = self._format_as_string(value)
        textwidget = self.widget
        # Workaround for pygtk bug in versions before 0.6.10.
        # pygtk_version doesn't exist prior to 0.6.8.
        self._block_handlers()
        textwidget.delete_text(0, textwidget.get_length())
        if getattr(gtk, "pygtk_version", (0,6,8)) < (0,6,10):
            # We need to call changed() because insert_defaults is broken,
            # which is quite bad as delete triggers it as well, so each
            # insertion triggers three signals. :-(
            textwidget.insert_defaults(text)
            textwidget.changed()
        else:
            textwidget.insert_text(text)
        self._unblock_handlers()
        return text

    def read(self):
        return self.widget.get_chars(0, self.widget.get_length())

