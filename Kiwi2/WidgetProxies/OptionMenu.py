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

from Kiwi.WidgetProxies.Base import MultiWidgetProxy

class OptionMenuProxy(MultiWidgetProxy):
    def __init__(self, proxy, widget, attr):
        MultiWidgetProxy.__init__(self, proxy, widget, attr)

        # Let the menu know it's in a proxy so it can notify us of
        # changes in its items -- see Menu.prefill(). This lets us avoid
        # having to call refresh_optionmenu.
        widget.set_data("_kiwi_proxy", (proxy, self.name))
        self.setup()

    def setup(self):
        menu = self.widget.get_menu()
        if not menu or len(menu.get_children()) == 0:
            return False
        items = menu.get_children()
        # connect signals; this is dangerous if refresh_optionmenu() is
        # called multiple times without an optionmenu.clear() between
        # them
        for item in items:
            self._connect(item, "activate", self.callback)
            # Set up data. If there is no data associated with the
            # optionmenu, store the label
            data = item.get_data("_kiwi_data") 
            if data != None:
                continue
            if item == menu.get_active():
                # The selected item is childless
                data = self._get_label(self.widget)
            elif not item.get_children():
                # Skip separators, which are also childless items
                continue
            else:
                # Get label of items children
                data = self._get_label(item)
            item.set_data("_kiwi_data", data) 

    def update(self, value):
        menu = self.widget.get_menu()
        if not menu or len(menu.get_children()) == 0:
            # Go back if nothing is in the menu, setting model to value
            # because we *may* be prefill()ed at a later moment. XXX: this
            # masks a serious error when we try to set the model to a value
            # and the optionmenu is empty.
            self.proxy._update_model(self, value)
            return False
        # if value is none, reset optionmenu to first entry 
        if value == None:
            self.widget.set_history(0)
            item = menu.get_active()
            position = -1
        else:
            item, position = self._get_item_by_value(value)
        if item:
            # This ugly hack is used when there is no need to change the
            # optionmenu's position. This only happens when the chosen
            # menuitem is already the default
            if position != -1:
                self.widget.set_history(position)
            self._block_handlers(item)
            item.activate()
            self._unblock_handlers(item)
            return self.read()

        # Build list of valid values, the ugly way<tm>
        valid = []
        for item in menu.get_children():
            data = item.get_data("_kiwi_data") 
            valid.append(data)
        raise ValueError, """Couldn't set value `%s' for widget %s
Valid values: %s\n
(Hint: this can happen if you are using an OptionMenu with some items
created in glade but doing a prefill() afterwards. If you are using
prefill, *never* have menuitems in glade or setting optionmenu data
won't work as expected. 

Note also that you can *not* use an empty string or 0 (zero) to indicate
you want the default selection; None is the *only* value that the Proxy
interprets as "unset" or "use default".)""" % (value, self.name, valid)

    def read(self, item=None):
        menu = self.widget.get_menu()
        if not menu or len(menu.get_children()) == 0:
            return None
        item = item or menu.get_active()
        data = item.get_data("_kiwi_data")
        if data is None:
            data = self._get_label(self.widget)
        return data

    def callback(self, item, *args):
        # There is an interesting reason why item needs to be passed in
        # to read(). When calling item.activate() manually, the callback
        # is called *before* the menu updates its history (very wierd)
        # -- this means that get_active() returns the stale item, not
        # the one just activate()d!
        self.proxy._update_model(self, self.read(item))

    def _get_label(self, item):
        return item.get_children()[0].get()
           
    def _get_item_by_value(self, value):
        # Returns a tuple (menuitem, position_in_menu), and
        # (False, -1) if not found.
        menu = self.widget.get_menu()
        # Go back if nothing is in the menu yet
        if not menu or len(menu.get_children()) == 0:
            return False, -1

        selected_item = menu.get_active()
        # If not a prefill()ed Kiwi.OptionMenu, this will be None
        selected_data = selected_item.get_data("_kiwi_data")
        if (selected_data != None and selected_data == value):
                # If the selected menuitem matches value, no need to do
                # anything. The -1 is an evil hack that means "don't update
                # the menu's position", and it's used because there is no
                # get_history() in GtkOptionMenu, and we would need it to
                # avoid doing a sequential scan in the menu.
                return selected_item, -1

        # Oh, why we need a counter? Just because set_active() and
        # get_active() and set_history() are TOTALLY INCONSISTENT
        counter = 0
        for item in menu.get_children():
            # Skip selected item; it doesn't have a label (ugh) so
            # it needs to be special cased
            if item == selected_item:
                counter = counter + 1
                continue
            this_data = item.get_data("_kiwi_data")
            if this_data == value:
                return item, counter
            counter = counter + 1

        # Bad bad batman; didn't find what we were looking for
        return False, -1

