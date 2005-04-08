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

from Kiwi2 import ValueUnset
from Kiwi2.initgtk import gtk, gobject
from Kiwi2.Widgets import WidgetProxy
from Kiwi2.Widgets.datatypes import ValidationError
from Kiwi2.utils import gsignal, gproperty, set_background, merge_colors

ERROR_COLOR = "#ffa5a5"
GOOD_COLOR = "white"

# amount of time until we complain if the data is wrong (seconds)
COMPLAIN_DELAY = 1

class Entry(gtk.Entry, WidgetProxy.MixInSupportMandatory):
    """The Kiwi Entry widget has many special features that extend the basic gtk entry.
    
    First of all, as every Kiwi Widget, it implements the Proxy protocol. As the users 
    types the entry can interact with the application model automaticly. 
    Kiwi Entry also implements intresting UI additions. If the input data does not match
    the data type of the entry the background nicely fades to a light red color. 
    As the background changes an information icon appears. When the user
    passes the mouse over the infomation icon a tooltip is displayed informing the
    user how to correctly fill the entry. When dealing with date and float data-type
    the information on how to fill these entries is displayed according to the 
    current locale.
    """
    WidgetProxy.implementsIProxy()
    WidgetProxy.implementsIMandatoryProxy()
    
    gsignal('changed', 'override')
    # mandatory widgets need to have this signal connected
    gsignal('expose-event', 'override')
    
    def __init__(self):
        gtk.Entry.__init__(self)
        WidgetProxy.MixInSupportMandatory.__init__(self)

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
        self._complaint_checker_id = -1

        self._error_tooltip = ErrorTooltip(self)

        # stores the position of the information icon
        self._info_icon_position = False
        
        # state variables
        self._draw_error_icon = False
        self._show_error_tooltip = False
        self._error_tooltip_visible = False
        
    def _check_entry(self):
        if len(self.get_text()) == 0 and self._mandatory:
            self._draw_mandatory_icon = True
        else:
            self._draw_mandatory_icon = False
        
    def do_changed(self):
        """Called when the content of the entry changes.

        Sets an internal variable that stores the last time the user
        changed the entry
        """
        
        self._last_change_time = time.time()

        self._check_entry()
            
        self.emit('content-changed')
        self.chain()
    
    def _get_cursor_position(self):
        """If the input is wrong (as consequence the icon is been displayed),
        this method reads the mouse cursor position and checks if it's on top of
        the information icon
        """
        if not self._info_icon_position:
            return True
        
        icon_x, icon_x_range, icon_y, icon_y_range = self._info_icon_position
        
        toplevel = self.get_toplevel()
        pointer_x, pointer_y = toplevel.get_pointer()
        
        if pointer_x not in icon_x_range or pointer_y not in icon_y_range:
            self._error_tooltip.disappear()
            return True
        
        if self._error_tooltip.visible():
            return True
            
        gdk_window = toplevel.window
        window_x, window_y = gdk_window.get_origin()
        entry_x, entry_y, entry_width, entry_height = self.get_allocation()
        tooltip_width, tooltip_height = self._error_tooltip.get_size()
        x = window_x + entry_x + entry_width - tooltip_width/2
        y = window_y + entry_y - entry_height
        self._error_tooltip.display(x, y)
        self._error_tooltip_visible = True 
                
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
                if self._complaint_checker_id == -1:
                    self._complaint_checker_id = \
                        gobject.idle_add(self._check_for_complaints)
                    self._get_cursor_position_id = \
                        gobject.timeout_add(200, self._get_cursor_position)
            data = None
        return data

    def update(self, data):
        WidgetProxy.MixInSupportMandatory.update(self, data)

        if data is ValueUnset:
            self.set_text("")
        else:
            WidgetProxy.MixInSupportMandatory.update(self, data)      
            self.set_text(self.type2str(data))

    def set_text(self, text):
        gtk.Entry.set_text(self, text)
        self.emit('content-changed')

    def _check_for_complaints(self):
        """Check for existing complaints and when to start complaining is case
        the input is wrong
        """
        if self._last_change_time is None:
            # the user has not started to type
            return True
        
        now = time.time()
        elapsed_time = now - self._last_change_time
        
        if elapsed_time < COMPLAIN_DELAY:
            return True
        
        if not self._invalid_data:
            return True
        
        # if we are already complaining, don't complain again
        if self._background_timeout_id != -1:
            return True
        
        self._show_error_tooltip = True
        self._draw_error_icon = True
        #self.queue_draw()
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
            gobject.source_remove(self._complaint_checker_id)
            # before removing the get_cursor_position idle we need to be sure
            # that the tooltip is not been displayed
            self._error_tooltip.disappear()
            gobject.source_remove(self._get_cursor_position_id)
            self._background_timeout_id = -1
            self._complaint_checker_id = -1
        set_background(self, GOOD_COLOR)
        self._draw_error_icon = False
       
       
    def do_expose_event(self, event):
        """Draw information icon and the mandatory icon"""
        
        result = self.chain(event)
        
        if self._draw_widget is None:
            # need to be defined so the _draw_icon knows where to draw
            # It needs to be called hear because before the window is not defined
            self.set_drawing_windows(self, self.window)
        
        
        if self._draw_error_icon:
            icon_x_pos, icon_y_pos, pixbuf_width, pixbuf_height = \
                      self._draw_icon(self, self.window, gtk.STOCK_DIALOG_INFO)
            
            kiwi_entry_name = self.get_name()
            
            icon_x_range = range(icon_x_pos, icon_x_pos + pixbuf_width)
            icon_y_range = range(icon_y_pos, icon_y_pos + pixbuf_height)
            self._info_icon_position = \
                [icon_x_pos, icon_x_range, icon_y_pos, icon_y_range]        
        
        elif self._draw_mandatory_icon:
            self._draw_icon(self, self.window)
        
        return result 
              
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
    
    def disappear(self):
        self.hide()
