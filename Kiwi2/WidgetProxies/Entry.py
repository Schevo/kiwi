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

from Kiwi2.WidgetProxies.Base import EditableProxy

class EntryProxy(EditableProxy):
    def __init__(self, proxy, widget, attr):
        EditableProxy.__init__(self, proxy, widget, attr)

        self._connect("changed", self.callback)

    def read(self):
        return self.widget.get_text()

    def _emit_changed_hack(self):
        self.widget.emit("changed")

class LabelProxy(EditableProxy):
    # Note that Label doesn't generate signals, so setting text to a
    # label *never* causes the model to update. If this is a bug, it's a
    # subtle one!
    def __init__(self, proxy, widget, attr):
        EditableProxy.__init__(self, proxy, widget, attr)
        # No need to init EntryProxy -- no signals for label :-) 

    def read(self):
        return self.widget.get_text()

class ComboProxy(EntryProxy):
    def __init__(self, proxy, widget, attr):
        self.combo = widget
        EntryProxy.__init__(self, proxy, widget.entry, attr)

# class KiwiComboProxy(ComboProxy):
#     # The Kiwi Combo allows data to be associated to the Combo: in the
#     # case that datadict is non-empty, we do the appropriate translations.
#     def update(self, value):
#         if value is None:
#             # this seems to only happen when setting a default or doing
#             # a new_model(). XXX: true?
#             self._block_handlers()
#             self.widget.set_text("")
#             self._unblock_handlers()
#         else:
#             if self.combo.datadict is None:
#                 # If no datadict exists, there is no magic translation
#                 # to be done because prefill() was never issued.
#                 return ComboProxy.update(self, value)
#             try:
#                 self.combo.select_item_by_data(value)
#             except KeyError, e:
#                 raise ValueError, e
#         return value
#     
#     def read(self):
#         value = self.widget.get_text()
#         if self.combo.datadict is None:
#             # If we're not using prefilled Combos, return the value
#             return value
#         if not self.combo.datadict:
#             # If no datadict exists, we probably have an empty list.
#             return None
#         return self.combo.datadict.get(value)
# 
# XXX XXX XXX
# class AutoComboProxy(KiwiComboProxy):
#     def update(self, value):
#         if not self.combo.datadict:
#             # Nothing in the list yet; no way to update for it,
#             # therefore.
#             return None
#         return KiwiComboProxy.update(self, value)
# 
#     def read(self):
#         return self.combo.get_selected()
# 

class SpinButtonProxy(EntryProxy):
    def set_format(self, format):
        EntryProxy.set_format(self, format)
        self.disable_numeric()

    def disable_numeric(self):
        # This is required because spinbuttons can't handle formatting.
        # It is called from two points: Proxies._setup_widgets and
        # set_format() above; these are the points which change the
        # Proxy to sending strings to the widget
        self.widget.set_numeric(0)

    def update(self, value):
        value = self._format_as_string(value)
        valuetype = type(value)
        old_text = self.read()
        self._block_handlers()
        if valuetype in (IntType, FloatType):
            # Use set_value for integers, since I *think* it's the
            # correct thing.
            self.widget.set_value(value)
        elif valuetype == StringType:
            print "OINK", value
            self.widget.set_text(value)
        else:
            raise TypeError(
                "Value %s for %s is of invalid type" % (value, self.name))
        if old_text == value:
            # XXX GTK+ change from 1.2 to 2.x
            self.widget.emit("changed")
        self._unblock_handlers()
        return value

