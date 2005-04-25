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

MANDATORY_ICON = gtk.STOCK_EDIT
INFO_ICON = gtk.STOCK_DIALOG_INFO

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
        
        # this attribute stores the info on where to draw icons and paint
        # the background
        # although we have our own draw method we still need to 
        # set this attribute because it is used to paint the background
        self._widget_to_draw = self
        
        # due to changes on pygtk 2.6 we have to make some ajustments here
        if gtk.pygtk_version < (2,6):
            self.do_expose_event = self.chain
    
    def _key_release_event(self, *args):
        self._last_change_time = time.time()
        self.emit('content-changed')

    def read(self):
        start = self.textbuffer.get_start_iter()
        end = self.textbuffer.get_end_iter()
        text = self.textbuffer.get_text(start, end)

        if not text.strip() and self._mandatory:
            self._draw_mandatory_icon = True
        else:
            self._draw_mandatory_icon = False
        
        data = self._validate_data(text)
        return data

    def update(self, data):
        # first, trigger some basic validation
        WidgetProxy.MixinSupportValidation.update(self, data)

        if data is ValueUnset:
            self.textbuffer.set_text("")
        else:
            self.textbuffer.set_text(self.type2str(data))

    def do_expose_event(self, event):
        """Expose-event signal are triggered when a redraw of the widget
        needs to be done.
        
        Draws information and mandatory icons when necessary
        """        
        result = gtk.TextView.do_expose_event(self, event)
        
        # this attribute stores the info on where to draw icons and paint
        # the background
        # although we have our own draw method we still need to 
        # set this attribute because it is used to paint the background
        self._gdkwindow_to_draw = self.get_window(gtk.TEXT_WINDOW_TEXT)
        
        self._draw_icon()
        
        return result
    
    def _draw_pixbuf(self, iconx, icony, pixbuf, pixw, pixh):
        area_window = self._gdkwindow_to_draw
        winw, winh = area_window.get_size()
        
        area_window.draw_pixbuf(None, pixbuf, 0, 0, 
                                (winw - pixw) / 2, (winh - pixh) / 2,
                                pixw, pixh)
        

gobject.type_register(TextView)
