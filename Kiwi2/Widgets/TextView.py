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

from Kiwi2.initgtk import gtk, gobject
from Kiwi2.Widgets import WidgetProxy
from Kiwi2.utils import gsignal, gproperty, set_foreground
from Kiwi2 import _warn, ValueUnset

class TextView(gtk.TextView, WidgetProxy.MixinSupportValidation):
    WidgetProxy.implementsIProxy()
    WidgetProxy.implementsIMandatoryProxy()
    
    # mandatory widgets need to have this signal connected
    gsignal('expose-event', 'override')
    
    def __init__(self):
        WidgetProxy.MixinSupportValidation.__init__(self)
        gtk.TextView.__init__(self)
        
        self.textbuffer = gtk.TextBuffer()
        self.set_buffer(self.textbuffer)
        
        self.connect("key-release-event", self._key_release_event)
        
    def _key_release_event(self, *args):
        self._last_change_time = time.time()
        self.emit('content-changed')

    def read(self):
        start = self.textbuffer.get_start_iter()
        end = self.textbuffer.get_end_iter()
        text = self.textbuffer.get_text(start, end)

        if text == "" and self._mandatory:
            self._draw_mandatory_icon = True
        else:
            self._draw_mandatory_icon = False
        
        data = self._check_data(text)
        return data

    def update(self, data):
        # first, trigger some basic validation
        WidgetProxy.MixinSupportValidation.update(self, data)

        if data is ValueUnset:
            self.textbuffer.set_text("")
        else:
            self.textbuffer.set_text(self.type2str(data))

    def _draw_icon(self, icon):
        """Draw an icon"""
        
        widget = self
        gdk_window = self.get_window(gtk.TEXT_WINDOW_TEXT)
        
        pixbuf, pixbuf_width, pixbuf_height = self._render_icon(icon)
        
        widget_x, widget_y, widget_width, widget_height = widget.get_allocation()            
        icon_x_pos = widget_x + widget_width - pixbuf_width
        icon_y_pos = widget_y + widget_height - pixbuf_height
        
        area_window = gdk_window
        gdk_window_width, gdk_window_height = area_window.get_size()
        
        draw_icon_x = (gdk_window_width - pixbuf_width) / 2
        draw_icon_y = (gdk_window_height - pixbuf_height) / 2
        area_window.draw_pixbuf(None, pixbuf, 0, 0, draw_icon_x,
                                     draw_icon_y, pixbuf_width,
                                     pixbuf_height)
        
        return (icon_x_pos, icon_y_pos, pixbuf_width, pixbuf_height)



gobject.type_register(TextView)
