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

import sys
import time

from Kiwi2 import _warn, ValueUnset
from Kiwi2.initgtk import gtk, gobject
from Kiwi2.Widgets import datatypes
from Kiwi2.utils import gsignal, gproperty, set_background, merge_colors
from Kiwi2.Widgets.datatypes import ValidationError


class Mixin(object):
    """This class is a mixin that provide a common interface for KiwiWidgets.

    Usually the Proxy class need to set and get data from the widgets. It also
    need a validation framework.
    """

    def __init__(self, data_type=str, model_attribute=None,
                 default_value=None):
        # we need initial values so this variables always exist
        self._default_value = None
        self._data_type = None
        self._model_attribute = None
        
        # now we setup the variables with our parameters
        self.set_data_type(data_type)
        self.set_model_attribute(model_attribute)
        self.set_default_value(default_value)
        
    def update(self, data):
        """Set the content of the widget with @data.

        The type of @data should match the data-type property. The two
        exceptions to this rule is ValueUnset and None. When the proxy
        call ourselves with these values we just do nothing. This probably
        means that the model is not initialized.
        """
        if data is ValueUnset or data is None:
            return
        
        elif not isinstance(data, self._data_type):
            raise TypeError("%s: Data is supposed to be a %s but it is %s: %s" \
                            % (self.name, self._data_type, type(data), data))

    def read(self):
        """Get the content of the widget.

        The type of the return value matches the data-type property.

        This returns None if the user input a invalid value
        """
        
    def do_get_property(self, pspec):
        prop_name = pspec.name.replace("-", "_")
        try:
            return getattr(self, "get_%s" % prop_name)()
        except AttributeError:
            raise AttributeError("Invalid property name: %s" % pspec.name)

    def do_set_property(self, pspec, value):
        prop_name = pspec.name.replace("-", "_")
        try:
            getattr(self, "set_%s" % prop_name)(value)
        except AttributeError:
            raise AttributeError("Invalid property name: %s" % pspec.name)
        
    def get_data_type(self):
        return self._data_type

    def set_data_type(self, data_type):
        """Set the data type for the widget
        
        data_type can be None, a type object or a string with the name of the
        type object, so None, "<type 'str'>" or 'str'
        """
        if data_type is None:
            self._data_type = None
            return

        error_msg = " is not supported. Supported types are: %s" % \
                    ', '.join(datatypes.supported_types_names)
        
        # we allow data_type to be a string with the name of the type
        if isinstance(data_type, basestring):
            if not data_type in datatypes.supported_types_names:
                raise TypeError("%s %s" % (data_type, error_msg))

            else:
                ind = datatypes.supported_types_names.index(data_type)
                self._data_type = datatypes.supported_types[ind]
                
        elif data_type not in datatypes.supported_types:
            raise TypeError("%s %s" % (data_type, error_msg))

        else:
            self._data_type = data_type

    def get_model_attribute(self):
        return self._model_attribute

    def set_model_attribute(self, attribute):
        self._model_attribute = attribute

    def get_default_value(self):
        return self._default_value

    def set_default_value(self, value):
        if isinstance(value, basestring):
            self._default_value = self.str2type(value)
        else:
            self._default_value = value
    
    def str2type(self, data):
        """Convert a string to our data type.

        This may raise exceptions if we can't do the conversion
        """
        if self._data_type is None:
            msg = "You must set the data type before converting a string"
            raise TypeError(msg)
        assert isinstance(data, basestring)
        # if the user clear the widget we should not raise a conversion error
        if data == '':
            return self._default_value
        return datatypes.converters[datatypes.FROM_STR][self._data_type](data)

    def type2str(self, data):
        """Convert a value to a string"""
        if self._data_type is None:
            msg = "You must set the data type before converting a type"
            raise TypeError(msg)
        assert isinstance(data, self._data_type)
        return datatypes.converters[datatypes.TO_STR][self._data_type](data)


ERROR_COLOR = "#ffa5a5"
GOOD_COLOR = "white"

MANDATORY_ICON = gtk.STOCK_FILE
INFO_ICON = gtk.STOCK_DIALOG_INFO

# amount of time until we complain if the data is wrong (seconds)
COMPLAIN_DELAY = 1


class MixinSupportValidation(Mixin):
    """Class used by some Kiwi Widgets that need to support mandatory 
    input and validation features such as custom validation and data-type
    validation.
    
    Mandatory support provides a way to warn the user when input is necessary.
    The validatation feature provides a way to check the data entered and to
    display information about what is wrong.
    """
    
    def __init__(self, data_type=str, model_attribute=None,
                 default_value=None):
        Mixin.__init__(self, data_type, model_attribute,
                                  default_value)
        self._mandatory = False
        self._draw_mandatory_icon = False
        
        self._draw_widget = None
        self._draw_gdk_window = None
        
        self._error_tooltip = ErrorTooltip(self)
        
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


        # stores the position of the information icon
        self._info_icon_position = False
        
        # state variables
        self._draw_info_icon = False
        self._show_error_tooltip = False
        self._error_tooltip_visible = False
    
        self._widget = None
        self._gdk_window = None
    
    def get_mandatory(self):
        """Checks if the Kiwi Widget is set to mandatory"""
        return self._mandatory
    
    def set_mandatory(self, mandatory):
        """Sets the Kiwi Widget as mandatory, in other words, the widget needs 
        to provide data to the widget 
        """
        self._mandatory = mandatory
        self._draw_mandatory_icon = mandatory
        self.queue_draw()

    def _define_icons_to_draw(self):
        
        if self._draw_info_icon:
            icon_x_pos, icon_y_pos, pixbuf_width, pixbuf_height = \
                      self._draw_icon(INFO_ICON)
            
            kiwi_entry_name = self.get_name()
            
            icon_x_range = range(icon_x_pos, icon_x_pos + pixbuf_width)
            icon_y_range = range(icon_y_pos, icon_y_pos + pixbuf_height)
            self._info_icon_position = \
                [icon_x_pos, icon_x_range, icon_y_pos, icon_y_range]
            
        elif self._draw_mandatory_icon:
            self._draw_icon(MANDATORY_ICON)

    def _validate_data(self, text):
        """Checks if the data is valid.
        
        Validates data-type and custom validation.
        text - needs to be a string
        returns the widget data-type
        """
        try:
            data = self.str2type(text)
            # this signal calls the on_widgetname__validate method of the 
            # view class and gets the exception (if any).
            error = self.emit("validate", data)
            if error:
                raise error
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
        self._draw_info_icon = True
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
        self._draw_info_icon = False

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

    def _draw_icon(self, icon):
        """Draw an icon"""
        
        if self._widget is None:
            return
        
        widget = self._widget
        gdk_window = self._gdk_window
        
        icon_x_pos, icon_y_pos, pixbuf, pixbuf_width, pixbuf_height = \
        self._render_icon(icon, widget)
        
        area_window = gdk_window.get_children()[0]
        gdk_window_width, gdk_window_height = area_window.get_size()
        
        draw_icon_x = gdk_window_width - pixbuf_width
        draw_icon_y = (gdk_window_height - pixbuf_height)/2
        area_window.draw_pixbuf(None, pixbuf, 0, 0, draw_icon_x,
                                     draw_icon_y, pixbuf_width,
                                     pixbuf_height)
        
        return (icon_x_pos, icon_y_pos, pixbuf_width, pixbuf_height)

    def _render_icon(self, icon, widget):
        pixbuf = self.render_icon(icon, gtk.ICON_SIZE_MENU)
        pixbuf_width = pixbuf.get_width()
        pixbuf_height = pixbuf.get_height()
        widget_x, widget_y, widget_width, widget_height = widget.get_allocation()
        
        icon_x_pos = widget_x + widget_width - pixbuf_width
        icon_y_pos = widget_y + widget_height - pixbuf_height
        
        return (icon_x_pos, icon_y_pos, pixbuf, pixbuf_width, pixbuf_height)


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


def implementsIProxy():
    """Add a content-changed signal and a data-type, default-value, 
    model-attribute properties to the class where this 
    functions is called.
    """
    frame = sys._getframe(1)
    try:
        local_namespace = frame.f_locals
    finally:
        del frame

    if not '__gsignals__' in local_namespace:
        dic = local_namespace['__gsignals__'] = {}
    else:
        dic = local_namespace['__gsignals__']

    dic['content-changed'] = (gobject.SIGNAL_RUN_LAST, None, ())
    
    # the line below is used for triggering custom validation.
    # if you want a custom validation on a widget make a method on the
    # view class for each widget that you want to validate.
    # the method signature is:
    # def on_widgetname__validate(self, widget, data)
    dic['validate'] = (gobject.SIGNAL_RUN_LAST, object, (object,))

    if not '__gproperties__' in local_namespace:
        dic = local_namespace['__gproperties__'] = {}
    else:
        dic = local_namespace['__gproperties__']

    dic['data-type'] = (object, 'data-type', 'Data Type',
                        gobject.PARAM_READWRITE)
    dic['model-attribute'] = (str, 'model-attribute', 'Model Attribute', '',
                              gobject.PARAM_READWRITE)
    dic['default-value'] = (object, 'default-value', 'Default Value',
                            gobject.PARAM_READABLE)

def implementsIMandatoryProxy():
    frame = sys._getframe(1)
    try:
        local_namespace = frame.f_locals
    finally:
        del frame

    dic = local_namespace['__gproperties__']
    dic['mandatory'] = (bool, 'mandatory', 'Mandatory', False,
                        gobject.PARAM_READWRITE)
