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

from Kiwi import ValueUnset
from Kiwi.WidgetProxies.Base import MultiWidgetProxy

class RadioGroupProxy(MultiWidgetProxy):
    def __init__(self, proxy, group, attr):

        # Convert radiogroup to something more solid
        newgroup = {}
        for button_name in group.keys():
            button = proxy._get_widget_by_name(button_name)
            data = group[button_name]
            if data == ValueUnset:
                # If the radiogroup was grouped using a list and not a
                # dict, use the button label
                data = button.get_children()[0].get()
            newgroup[button] = data

        # we use group for widgets here, since there is no main widget
        MultiWidgetProxy.__init__(self, proxy, newgroup, attr)

        for button in newgroup.keys():
            self._connect(button, "clicked", self.callback)

    def update(self, value):
        # If value is none, use currently selected option
        if value == None: 
            value = self.read()
        button = self._get_radiobutton_by_value(value)
        if not button:
            msg = "Value %s is not valid for this radiogroup" + \
                  ", should be one of:\n%s" 
            raise ValueError, msg % (value, group.values())
        self._block_handlers(button)
        button.clicked()
        self._unblock_handlers(button)
        return value

    def read(self):
        for button, value in self.widget.items():
            if button.get_active():
                return value
        raise AssertionError, "no active button for radiogroup %s" % self.name

    def callback(self, button, *args):
        # Both the button being selected and the one being deselected
        # emit clicked, so we need to check if it's active or not
        if button.get_active():
            self.proxy._update_model(self, self.widget[button])

    def _get_radiobutton_by_value(self, value):
        group = self.widget
        for button, button_value in self.widget.items():
            if value == button_value:
                return button
        msg = "Value %s is not valid for radiogroup %s;" + \
              "\nit should be one of %s"
        raise ValueError, msg % (repr(value), self.name, group.values())

