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

import string
from types import IntType, FloatType, StringType

from Kiwi import USE_MX, ValueUnset

class ConversionError(Exception): pass

if USE_MX:
    from mx.DateTime import DateTimeType, DateTimeFrom, strptime
    from mx.DateTime import Error as DateTimeError

class WidgetProxy:
    block = False
    # XXX: only used in EditableProxy, but needs to be defined for all
    format = None
    datetime = False
    numeric = False
    converted = False
    def __init__(self, proxy, widget, name):
        self.proxy = proxy
        self.widget = widget
        self.name = name

        self.signal_ids = []

    def callback(self, *args):
        state = self.read()
        self.proxy._update_model(self, state)

    def _connect(self, signal, handler, *args):
        id = apply(self.widget.connect_after, (signal, handler) + args)
        self.signal_ids.append(id)

    # Block and unblock handlers exist to avoid having the handlers loop
    # when updating themselves. They are only used when the model
    # updates the proxies using through the Proxy.update() method. They
    # could be called _[un]block_handlers_if_needed(), I guess.

    def _block_handlers(self):
        if not self.block:
            return
        for id in self.signal_ids:
            self.widget.handler_block(id)
    
    def _unblock_handlers(self):
        if not self.block:
            return
        for id in self.signal_ids:
            self.widget.handler_unblock(id)

#
#
#

class MultiWidgetProxy(WidgetProxy):
    """
    Special class used in OptionMenu and RadioGroups, which have
    multiple widgets for each WidgetProxy instance.
    """
    def __init__(self, proxy, widget, name):
        WidgetProxy.__init__(self, proxy, widget, name)
        # For MultiWidgetProxy, we use a hash instead of a list
        self.signal_ids = {}

    def _connect(self, widget, signal, handler, *args):
        signals = self.signal_ids
        if not signals.has_key(widget):
            signals[widget] = []
        id = apply(widget.connect_after, (signal, handler) + args)
        self.signal_ids[widget].append(id)

    def _block_handlers(self, widget):
        if not self.block:
            return
        for id in self.signal_ids[widget]:
            self.widget.signal_handler_block(id)

    def _unblock_handlers(self, widget):
        if not self.block:
            return
        for id in self.signal_ids[widget]:
            self.widget.signal_handler_unblock(id)

#
# For editables, which have type conversions and formatting
#

class EditableProxy(WidgetProxy):
    def set_numeric(self, bool=True):
        self.converted = self.numeric = bool

    def set_datetime(self, bool=True):
        self.converted = self.datetime = bool

    def set_format(self, format):
        self.format = format

    def update(self, value):
        text = self._format_as_string(value)
        old_text = self.read()
        self._block_handlers()
        self.widget.set_text(text)
        if text == old_text:
            self._emit_changed_hack()
        self._unblock_handlers()
        return value

    def _emit_changed_hack(self):
        # Hack required because GTK+ no longer emits the changed signal
        # when we issue a set_text() with the same string as the current
        # Entry/SpinButton's content.
        pass

    def read_converted(self, value=ValueUnset):
        if value is ValueUnset:
            value = self.read()

        if USE_MX and self.datetime:
            try:
                value = self._get_datetime(value)
            except DateTimeError:
                if self.proxy._conversion_errors:
                    raise ConversionError, "Unconvertible value %r" % value
                # If we got an invalid date, set the model value to
                # None. This is harsh, but more correct (the other
                # option would be not updating it at all, leaving
                # us with stale date)
                value = None
            return value

        if self.numeric:
            try:
                value = self._get_numeric(value)
            except ValueError:
                if self.proxy._conversion_errors:
                    raise ConversionError, "Unconvertible value %r" % value
                value = None
            return value
        
        raise AssertionError
    
    def _get_datetime(self, value=ValueUnset):
        if value is ValueUnset:
            value = self.read()
        if self.format:
            return strptime(value, self.format)
        else:
            # XXX: what if this goes wrong? :-)
            return DateTimeFrom(value)
    
    def _get_numeric(self, value=ValueUnset):
        if value is ValueUnset:
            value = self.read()
        value = string.strip(str(value))
        # we don't have a complete number yet
        if value in ("-","+","",None):
            return 0
        if self.proxy._decimal_separator:
            value = self._unconvert_decimals(value)
        try:
            value = int(value)
        except ValueError: 
            value = float(value)
            # Callers of this function need to catch the exception
        return value

    def _format_as_string(self, value):
        # Converts from a model value to a string. This is used just
        # before putting data into a text widget (entry, label and
        # gtktext). Note that spinbutton is a bit more complicated to
        # handle, not properly supported yet.

        # All values can be subject to conversion (except for None and
        # the empty string, which doesn't make much sense). Only numeric
        # attributes set to float values are subject to decimal
        # separator conversion, and only if a special decimal separator
        # is set.
      
        if value == "" or value is None:
            return ""

        valuetype = type(value)

        is_number = valuetype in (IntType, FloatType)
        # When set_numeric, is_number is *usually* true, but if the
        # default widget value is being used you might get the
        # occasional string, and we allow it.
        valid_type = valuetype in (IntType, FloatType, StringType)

        # Try DateTime first
        if USE_MX:
            if valuetype == DateTimeType:
                if self.datetime:
                    valid_type = 1
                else: 
                    raise TypeError, ("%s needs to be set_datetime(); "
                                      "an unexpected DateTime value %s "
                                      "was found""" % (self.name, value))
            elif self.datetime:
                raise TypeError, ("%s set as DateTime, but has non-datetime "
                                  "value %r" % (self.name, value))

        if not valid_type:
            raise TypeError, ("failed converting %s '%s' to string. Only "
                              "None, DateTime, string, ints and float are "
                              "allowed""" % (valuetype, str(value)))

        if self.format:
            try:
                if USE_MX and self.datetime:
                    value = value.strftime(self.format)
                else:
                    value = self.format % value
            except TypeError, e:
                raise TypeError, ("Failed to convert the contents of %r: "
                                  "The format string %r can't convert "
                                  "the data %r %r.  Did you forget to call "
                                  "set_numeric(), or are the arguments to "
                                  "set_format() incorrect?" % (self.name, 
                                  self.format, repr(value), type(value)))

        # if using a decimal separator, convert all numbers, whether
        # numeric or not
        if is_number and self.proxy._decimal_separator != None:
            value = self._convert_decimals(value)

        return str(value)

    def _convert_decimals(self, value):
        separator = self.proxy._decimal_separator
        if type(value) == StringType:
            # only convert if necessary
            if string.find(value, separator) > string.find(value, "."):
                return value
        return self._do_decimal_swap(value)

    def _unconvert_decimals(self, value):
        separator = self.proxy._decimal_separator
        if type(value) != StringType:
            return value
        # only unconvert if necessary
        if string.find(value, ".") > string.find(value, separator):
            return value
        return self._do_decimal_swap(value)

    def _do_decimal_swap(self, value):
        trans = self.proxy._decimal_translator
        value = str(value)
        return string.translate(value, trans)

