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

from Kiwi2.initgtk import gobject
from Kiwi2.Widgets import converters, TO_STR, FROM_STR
from Kiwi2.Widgets import supported_types, supported_types_names
from Kiwi2.Widgets import default_values

import sys

class WidgetProxyMixin(object):
    """This class is a mixin that provide a common interface for KiwiWidgets.

    Usually the Proxy class need to set and get data from the widgets. It also
    need a validation framework.
    """

    def __init__(self, data_type=None, model_attribute=None,
                 default_value=None):
        self._default_value = default_value
        self.set_data_type(data_type)
        self.set_model_attribute(model_attribute)
        
    def update(self, data):
        """Set the content of the widget with @data.

        The type of @data should match the data-type property
        """
        if self._data_type is None:
            msg = "You must set the data type before updating a Kiwi widget"
            raise TypeError, msg

        dt = supported_types_names.index(self._data_type)
        if not isinstance(data, supported_types[dt]):
            raise TypeError, "Data is supposed to be a %s but it is %s: %s" % \
                  (self._data_type, type(data), data)

    def read(self):
        """Get the content of the widget.

        The type of the return value matches the data-type property
        """
        
    def do_get_property(self, pspec):
        prop_name = pspec.name.replace("-", "_")
        try:
            return getattr(self, "get_%s" % prop_name)()
        except AttributeError:
            raise AttributeError, "Invalid property name: %s" % pspec.name

    def do_set_property(self, pspec, value):
        prop_name = pspec.name.replace("-", "_")
        try:
            getattr(self, "set_%s" % prop_name)(value)
        except AttributeError:
            raise AttributeError, "Invalid property name: %s" % pspec.name
        
    def get_data_type(self):
        return self._data_type

    def set_data_type(self, data_type):
        if data_type is None:
            self._data_type = None
            return
        
        if data_type not in supported_types_names:
            raise TypeError, "%s is not supported. Supported types are: %s" % \
                  (data_type, ','.join(supported_types_names))
        self._data_type = data_type

        # if we don't have a default value, get one from the default table
        if self._default_value is None:
            self._default_value = default_values[self._data_type]

    def get_model_attribute(self):
        return self._model_attribute

    def set_model_attribute(self, attribute):
        self._model_attribute = attribute

    def get_default_value(self):
        return self._default_value
    
    def str2type(self, data):
        """Convert a string to our data type.

        This may raise exceptions if we can't do the conversion
        """
        if self._data_type is None:
            msg = "You must set the data type before converting a string"
            raise TypeError, msg
        assert isinstance(data, basestring)
        # if the user clear the widget we should not raise a conversion error
        if data == '':
            return self._default_value
        return converters[FROM_STR][self._data_type](data)

    def type2str(self, data):
        """Convert a value to a string"""
        if self._data_type is None:
            msg = "You must set the data type before converting a type"
            raise TypeError, msg
        dt = supported_types_names.index(self._data_type)
        assert isinstance(data, supported_types[dt])
        return converters[TO_STR][self._data_type](data)

def implementsIProxy():
    """Add a content-changed signal and a data-type, default-value and
    model-attribute properties to the class where this functions is called.
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

    dic['data-type'] = (str, 'data-type', 'Data Type', '',
                        gobject.PARAM_READWRITE)
    dic['model-attribute'] = (str, 'model-attribute', 'Model Attribute', '',
                              gobject.PARAM_READWRITE)
    dic['default-value'] = (object, 'default-value', 'Default Value',
                            gobject.PARAM_READABLE)
