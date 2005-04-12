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

from Kiwi2 import _warn, ValueUnset
from Kiwi2.initgtk import gtk, gobject
from Kiwi2.Widgets import datatypes
from Kiwi2.utils import gsignal, gproperty

import sys

class MixIn(object):
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

class MixInSupportMandatory(MixIn):
    """Class used by some Kiwi Widgets that need to support mandatory input.
    
    If you need to create a Kiwi Widget with mandatory input support, use this
    class instead of WidgetProxyMinIn. Mandatory support provides a way to 
    warn the user when input is necessary.
    """
    
    MANDATORY_ICON = gtk.STOCK_FILE
    
    def __init__(self, data_type=str, model_attribute=None,
                 default_value=None):
        MixIn.__init__(self, data_type, model_attribute,
                                  default_value)
        self._mandatory = False
        self._draw_mandatory_icon = False
        
        self._draw_widget = None
        self._draw_gdk_window = None
    
    def set_drawing_windows(self, widget, gdk_window):
        """Set the widget and the gdk window to draw the icon.
        
        Sometimes the widget and gdk window to draw are not so obvious
        so we let the Kiwi Widget decide where to draw.
        """
        self._draw_widget = widget
        self._draw_gdk_window = gdk_window
    
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
    
    def _draw_icon(self, widget=None, gdk_window=None, icon=MANDATORY_ICON):
        """Draw an icon on a specified widget"""
        if widget is None:
            if self._draw_widget is None:
                _warn("Can't draw icon. %s widget needs to specify"
                " a widget to the draw function. If you want to"
                " draw the mandatory icon call set_drawing_window()"
                " with the correct parameters" % self.get_name())
                return
            else:
                widget = self._draw_widget
                gdk_window = self._draw_gdk_window
        
        
        pixbuf = widget.render_icon(icon, gtk.ICON_SIZE_MENU)
        pixbuf_width = pixbuf.get_width()
        pixbuf_height = pixbuf.get_height()
        
        widget_x, widget_y, widget_width, widget_height = widget.get_allocation()            
        icon_x_pos = widget_x + widget_width - pixbuf_width
        icon_y_pos = widget_y + widget_height - pixbuf_height
        
        area_window = gdk_window.get_children()[0]
        gdk_window_width, gdk_window_height = area_window.get_size()
    
        draw_icon_x = gdk_window_width - pixbuf_width
        draw_icon_y = (gdk_window_height - pixbuf_height)/2
        area_window.draw_pixbuf(None, pixbuf, 0, 0, draw_icon_x,
                                     draw_icon_y, pixbuf_width,
                                     pixbuf_height)
        
        return (icon_x_pos, icon_y_pos, pixbuf_width, pixbuf_height)        

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
