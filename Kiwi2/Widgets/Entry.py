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
    """The Kiwi Entry widget has special features that warns the user when the 
    input is wrong. If the input data does not match the data type of the entry the
    background of the entry turn red and a information icon appears. When the user
    passes the mouse over the infomation icon a tooltip is displayed informing the
    user how to correctly fill the entry. If the input is wrong the warning events
    happen after the the time specified by the COMPLAIN_DELAY constant.
    """
    implementsIProxy()
    gsignal('changed', 'override')
    gsignal('expose-event', 'override')
    
    def __init__(self):
        gtk.Entry.__init__(self)
        WidgetProxyMixin.__init__(self)

        # this flag means the data in the entry does not validate
        self._invalid_data = False

        # this is the last time the user changed the entry
        self._last_change_time = None

        self._validation_error_message = ""
        
        # id that paints the background red
        self._background_timeout_id = -1
        # id for idle that checks the cursor position
        self._get_cursor_position_id = -1
        # id for the idle that check if we should complain
        self._complain_checker_id = -1

        self._error_tooltip = ErrorTooltip(self)
        
        self._icon_display_dic = {}
        self._draw_error_icon = False
        self._show_error_tooltip = False
        self._error_tooltip_visible = False
        
        
    def do_changed(self):
        """Called when the content of the entry changes.

        Set's adn internal variable the stores the last time the user
        changed the entry
        """
        self._last_change_time = time.time()

        self.emit('content-changed')
        self.chain()
    
    def do_expose_event(self, event):
        """This method is called by the expose-event signal.

        This signal is emmited when the window is redrawn. If the data on the
        entry is wrong the information icon is drawn together.
        """
        result = self.chain(event)
        # draw icon
        if self._draw_error_icon:
            pixbuf = self.render_icon(gtk.STOCK_DIALOG_INFO, gtk.ICON_SIZE_MENU)
            pixbuf_width = pixbuf.get_width()
            pixbuf_height = pixbuf.get_height()
            
            entry_x, entry_y, entry_width, entry_height = self.get_allocation()            
            icon_x_pos = entry_x + entry_width - pixbuf_width
            icon_y_pos = entry_y + entry_height - pixbuf_height
            
            text_area_window = self.window.get_children()[0]
            width, height = text_area_window.get_size()
            text_area_window.draw_pixbuf(None, pixbuf, 0, 0, width - pixbuf_width, (height - pixbuf_height)/2, pixbuf_width, pixbuf_height)
            kiwi_entry_name = self.get_name()
            
            icon_x_range = range(icon_x_pos, icon_x_pos + pixbuf_width)
            icon_y_range = range(icon_y_pos, icon_y_pos + pixbuf_height)
            self._icon_display_dic[kiwi_entry_name] = [icon_x_pos, icon_x_range, icon_y_pos, icon_y_range]
        
        return result 
                
    def _get_cursor_position(self):
        """If the input is wrong (as consequence the icon is been displayed),
        this method reads the cursor position and checks if it's on top
        """
        kiwi_entry_name = self.get_name()
        try:
            icon_x, icon_x_range, icon_y, icon_y_range = self._icon_display_dic[kiwi_entry_name]
        except:
            # still no icons been displayed
            return True
        toplevel = self.get_toplevel()
        pointer_x, pointer_y = toplevel.get_pointer()
        # show or not the tooltip
        if pointer_x in icon_x_range and pointer_y in icon_y_range:
            if not self._error_tooltip.visible() and self._draw_error_icon:
                if kiwi_entry_name in self._icon_display_dic.keys():
                    gdk_window = toplevel.window
                    window_x, window_y = gdk_window.get_origin()
                    entry_x, entry_y, entry_width, entry_height = self.get_allocation()
                    tooltip_width, tooltip_height = self._error_tooltip.get_size()
                    x = window_x + entry_x + entry_width - tooltip_width/2
                    y = window_y + entry_y - entry_height
                    self._error_tooltip.display(x, y)
                    self._error_tooltip_visible = True
        else:
            self._error_tooltip.dissapear()
        
        return True
        
    def read(self):
        """Called after each caracter is typed. If the input is wrong start 
        complaining
        """
        text = self.get_text()
        try:
            data = self.str2type(text)
            # if the data is good we don't wait for the idle to inform
            # the user
            self._stop_complaining()
        except ValidationError, e:
            if not self._invalid_data:
                self._invalid_data = True
                self._validation_error_message = str(e)
                self._error_tooltip.set_error_text(self._validation_error_message)
                if self._complain_checker_id == -1:
                    self._complain_checker_id = gobject.idle_add(self._check_for_complains)
                    self._get_cursor_position_id = gobject.timeout_add(500, self._get_cursor_position)
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
        """Check for existing complains and when to start complaining is case
        the input is wrong
        """
        if self._last_change_time is None:
            # the user has not started to type
            return True
        
        now = time.time()
        elapsed_time = now - self._last_change_time
        if elapsed_time > COMPLAIN_DELAY:
            if self._invalid_data:
                # if we are already complaining, don't complain again
                if self._background_timeout_id == -1:
                    self._show_error_tooltip = True
                    self._draw_error_icon = True
                    self.queue_draw()
                    t_id = gobject.timeout_add(100, merge_colors(self, GOOD_COLOR, ERROR_COLOR).next)
                    self._background_timeout_id = t_id
                    
        return True # call back us again please

    def _stop_complaining(self):
        """If the input is corrected this method stop some activits that
        where necessary while complaining"""
        self._invalid_data = False
        # if we are complaining
        if self._background_timeout_id != -1:
            gobject.source_remove(self._background_timeout_id)
            gobject.source_remove(self._complain_checker_id)
            # before removing the get_cursor_position idle we need to be sure
            # that the tooltip is not been displayed
            self._error_tooltip.dissapear()
            gobject.source_remove(self._get_cursor_position_id)
            self._background_timeout_id = -1
            self._complain_checker_id = -1
        set_background(self, GOOD_COLOR)
        self._draw_error_icon = False
       
gobject.type_register(Entry)
    
class ErrorTooltip(gtk.Window):
    """Small tooltip window that popup when the user click on top of the error (information) icon"""
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

    def set_error_text(self, text):
        self.label.set_text(text)
    
    def display(self, x, y):
        self.move(x, y)
        self.show_all()
        
    def visible(self):
        return self.get_property("visible")
    
    def dissapear(self):
        self.hide()
