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
from Kiwi2.Widgets.WidgetProxy import WidgetProxyMixin, implementsIProxy
from Kiwi2.Widgets.datatypes import ValidationError
from Kiwi2.utils import gsignal, set_background, merge_colors

ERROR_COLOR = "#ffa5a5"
GOOD_COLOR = "white"

# amount of time until we complain if the data is wrong (seconds)
COMPLAIN_DELAY = 1

class Entry(gtk.Entry, WidgetProxyMixin):
    implementsIProxy()
    gsignal('changed', 'override')
    
    def __init__(self):
        gtk.Entry.__init__(self)
        WidgetProxyMixin.__init__(self)

        # this flag means the data in the entry does not validate
        self._invalid_data = False

        # this is the last time the user changed the entry
        self._last_change_time = None


        self._validation_error_message = ""
        
        self._background_timeout_id = -1

        # id for the idle that check if we should complain
        self._complain_checker_id = -1

        # we use the focus events to connect and disconnect the checker idle
        self.connect('focus-in-event', self._on_focus_in_event)
        self.connect('focus-out-event', self._on_focus_out_event)

        self._error_tooltip = ErrorTooltip(self)

    def do_changed(self):
        self._last_change_time = time.time()

        self.emit('content-changed')
        self.chain()
        
    def read(self):
        text = self.get_text()
        try:
            data = self.str2type(text)
            # if the data is good we don't wait for the idle to tell inform
            # the user
            self._stop_complaining()
        except ValidationError, e:
            if not self._invalid_data:
                self._invalid_data = True
                self._validation_error_message = str(e)

            data = None
        return data

    def update(self, data):
        if data is None:
            self.set_text("")
        else:
            WidgetProxyMixin.update(self, data)
        
            self.set_text(self.type2str(data))

    def set_text(self, text):
        gtk.Entry.set_text(self, text)
        self.emit('content-changed')

    def _check_for_complains(self):
        if self._last_change_time is None:
            # the user has not started to type
            return True

        now = time.time()
        elapsed_time = now - self._last_change_time
        if elapsed_time > COMPLAIN_DELAY:
            if self._invalid_data:
                # if we are already complaining, don't complain again
                if self._background_timeout_id == -1:
                    t_id = gobject.timeout_add(100,
                                               merge_colors(self, GOOD_COLOR,
                                                            ERROR_COLOR).next)
                    
                    self._background_timeout_id = t_id

                self._error_tooltip.update()

        return True # call back us again please

    def _stop_complaining(self):
        self._invalid_data = False
        if self._background_timeout_id != -1:
            gobject.source_remove(self._background_timeout_id)
            self._background_timeout_id = -1
        set_background(self, GOOD_COLOR)           
        self._error_tooltip.dissapear()
        
    def _on_focus_in_event(self, widget, event):
        if self._complain_checker_id == -1:
            cci = gobject.idle_add(self._check_for_complains)
            self._complain_checker_id = cci
 
    def _on_focus_out_event(self, widget, event):
        if not self._invalid_data:
            gobject.source_remove(self._complain_checker_id)
        
gobject.type_register(Entry)

class ErrorTooltip(gtk.Window):
    """Small tooltip window that popup when the user input bad data and softly
    dissapear after some seconds
    """
    def __init__(self, widget):
        gtk.Window.__init__(self, gtk.WINDOW_POPUP)

        self._widget = widget
        
        eventbox = gtk.EventBox()
        set_background(eventbox, "#fcffcd")

        alignment = gtk.Alignment()
        alignment.set_border_width(4)
        self.label = gtk.Label()
        alignment.add(self.label)
        eventbox.add(alignment)
        self.add(eventbox)

        self._timeout_id = -1

    def update(self):
        self.label.set_text(self._widget._validation_error_message)
        toplevel = self._widget.get_toplevel()
        gdk_window = toplevel.window
        x, y = gdk_window.get_origin()

        wx, wy, width, height = self._widget.get_allocation()

        self.move(x + wx, y + wy - height)
        self.show_all()

        if self._timeout_id == -1:
            self._timeout_id = gobject.timeout_add(5000, self.dissapear)

    def dissapear(self):
        self.hide()
        self._timeout_id = -1
        return False
