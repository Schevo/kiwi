#
# Kiwi: a Framework and Enhanced Widgets for Python
#
# Copyright (C) 2003-2005 Async Open Source
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
#            Lorenzo Gil Sanchez <lgs@sicem.biz>
#            Johan Dahlin <jdahlin@async.com.br>
#            Gustavo Rahal <gustavo@async.com.br>
#            Daniel Saran R. da Cunha <daniel@async.com.br>
#            Evandro Vale Miquelito <evandro@async.com.br>
#

"""Defines enhanced versions of GtkComboBox and GtkComboBoxEntry"""

import time

import gobject
import gtk
import gtk.keysyms 

from Kiwi2 import ValueUnset
from Kiwi2.datatypes import ValidationError
from Kiwi2.Widgets import WidgetProxy
from Kiwi2.utils import gsignal, gproperty

(COL_COMBO_LABEL,
 COL_COMBO_DATA) = range(2)

__pychecker__ = 'no-classattr'

class ComboProxyMixin(object):
    """Our combos always have one model with two columns, one for the string
    that is displayed and one for the object it cames from.
    """
    def __init__(self):
        """Call this constructor after the Combo one"""
        model = gtk.ListStore(str, object)
        self.set_model(model)

    def __len__(self):
        return len(self.get_model())
    
    def prefill(self, itemdata, sort=False):
        """Fills the Combo with listitems corresponding to the itemdata
        provided.
        
        Parameters:
        - itemdata is a list of strings or tuples, each item corresponding
        to a listitem. The simple list format is as follows::

          [ label0, label1, label2 ]
      
          If you require a data item to be specified for each item, use a
          2-item tuple for each element. The format is as follows::

          [ ( label0, data0 ), (label1, data1), ... ]

        - Sort is a boolean that specifies if the list is to be sorted by
        label or not. By default it is not sorted
        """
        if not isinstance(itemdata, (list, tuple)):
            raise TypeError("'data' parameter must be a list or tuple of item "
                            "descriptions, found %s") % type(itemdata)

        if len(itemdata) == 0:
            self.clear()
            return
        
        if sort:
            # we can't sort tuples
            if isinstance(itemdata, tuple):
                itemdata = list(itemdata)
                
            if isinstance(itemdata[0], str):
                itemdata.sort()
            else:
                itemdata.sort(lambda x, y: cmp(x[0], y[0]))

        model = self.get_model()

        values = []
        for item in itemdata:
            if isinstance(item, str):
                text, data = item, None
            elif isinstance(item, (list, tuple)):
                text, data = item
            else:
                raise TypeError("Incorrect format for itemdata; see "
                                "docstring for more information")

            if text in values:
                raise KeyError("Tried to insert duplicate value "
                               "%s into Combo!" % item)

            values.append(text)
            model.append((text, data))

    def append_item(self, label, data=None):
        """ Adds a single item to the Combo. Takes:
        - label: a string with the text to be added
        - data: the data to be associated with that item
        """
        if not isinstance(label, str):
            raise TypeError("label must be string, found %s" % label)
        model = self.get_model()
        model.append((label, data))

    def clear(self):
        """Removes all items from list"""
        model = self.get_model()
        model.clear()

    def select_item_by_position(self, pos):
        self.set_active(pos)

    def select_item_by_label(self, label):
        model = self.get_model()
        for row in model:
            if row[COL_COMBO_LABEL] == label:
                self.set_active_iter(row.iter)
                break
        else:
            raise KeyError("No item correspond to label %s in the combo %s"
                           % (label, self.name))
    
    def select_item_by_data(self, data):
        model = self.get_model()
        for row in model:
            if row[COL_COMBO_DATA] == data:
                self.set_active_iter(row.iter)
                break
        else:
            if len(model) and row[COL_COMBO_DATA] is None:
                #the user only prefilled the combo with strings
                self.select_item_by_label(data)
            else:
                raise KeyError("No item correspond to data %r in the combo %s" 
                               % (data, self.name))
            
    def get_model_items(self):
        model = self.get_model()
        items = {}
        for row in model:
            items[row[COL_COMBO_LABEL]] = row[COL_COMBO_DATA]
        
        return items

    def get_selected_label(self):
        iter = self.get_active_iter()
        if iter:
            model = self.get_model()
            return model.get_value(iter, COL_COMBO_LABEL)

    def get_selected_data(self):
        iter = self.get_active_iter()
        if iter:
            model = self.get_model()
            data = model.get_value(iter, COL_COMBO_DATA)
            if data is None:
                #the user only prefilled the combo with strings
                return model.get_value(iter, COL_COMBO_LABEL)
            return data
    
class ComboBox(gtk.ComboBox, ComboProxyMixin, WidgetProxy.Mixin):
    WidgetProxy.implementsIProxy()
    gsignal('changed', 'override')
    
    def __init__(self):
        WidgetProxy.Mixin.__init__(self)
        gtk.ComboBox.__init__(self)
        ComboProxyMixin.__init__(self)

        renderer = gtk.CellRendererText()
        self.pack_start(renderer)
        self.add_attribute(renderer, 'text', 0)

    def do_changed(self):
        self.emit('content-changed')
        self.chain()
 
    def read(self):
        data = self.get_selected_data()
        if data is not None:
            return data

    def update(self, data):
        # We dont need validation because the user always choose a valid value
        if data is not ValueUnset and data is not None:
            self.select_item_by_data(data)

    def prefill(self, itemdata, sort=False):
        ComboProxyMixin.prefill(self, itemdata, sort)
    
        # we always have something selected, by default the first item
        self.set_active(0)
        self.emit('content-changed')

    def clear(self):
        ComboProxyMixin.clear(self) 
    
gobject.type_register(ComboBox)

class ComboBoxEntry(gtk.ComboBoxEntry, ComboProxyMixin, 
                    WidgetProxy.MixinSupportValidation):
    WidgetProxy.implementsIProxy()
    WidgetProxy.implementsIMandatoryProxy()
    
    # it doesn't make sense to connect to this signal
    # because we want to monitor the entry of the combo
    # not the combo box itself.
    #gsignal('expose-event', 'override')
    
    gsignal('changed', 'override')
    
    gproperty("list-writable", bool, False, 
              "List Writable", gobject.PARAM_READWRITE)
    
    def __init__(self):
        gtk.ComboBoxEntry.__init__(self)
        WidgetProxy.MixinSupportValidation.__init__(self,
                                                    widget=self.child)
        ComboProxyMixin.__init__(self)

        self.set_text_column(0)
        # here we connect the expose-event signal directly to the entry
        self.child.connect('expose-event', self._on_child_entry__expose_event)

        # there are two 'changed' signals we need to care about:
        # 1) changed on the Combo (we override that signal)
        # 2) changed on the Entry (we connect to that signal here)
        self.child.connect('changed', self._on_child_entry__changed)

        # HACK! we force a queue_draw because when the window is first
        # displayed the icon is not drawn.
        gobject.idle_add(self.queue_draw)
        
        self.set_events(gtk.gdk.KEY_RELEASE_MASK)
        self.connect("key-release-event", self._on__key_release_event)
    
        self._list_writable = False
    
    def get_list_writable(self):
        return self._list_writable
    
    def set_list_writable(self, writable):
        self._list_writable = writable
    
    def _update_selection(self, text=None):
        if text is None:
            text = self.child.get_text()
        
        self.select_item_by_label(text)
    
    def _add_text_to_combo_list(self):
        text = self.child.get_text()
        if not text.strip():
            return
        items = self.get_model_items()
        if text not in items.keys():
            self.append_item(text)
            self._update_selection(text)
     
    def do_changed(self):
        self._last_change_time = time.time()
        self.emit('content-changed')
        self.chain()
    
    def _on__key_release_event(self, widget, event):
        """Checks for "Enter" key presses and add the entry text to 
        the combo list if the combo list is set as editable.
        """
        if not self._list_writable:
            return
        if event.keyval in (gtk.keysyms.KP_Enter, gtk.keysyms.Return):
            self._add_text_to_combo_list()
        
        # we call read here because "Enter" key press does 
        # not trigger entry_changed
        self.read()
        
    def _on_child_entry__expose_event(self, widget, event):
        # this attributes stores the info on were to draw icons and paint
        # the background
        # it's been defined here because it's when we have gdk window available
        self._draw_icon(self.child.window)

    def _on_child_entry__changed(self, widget):
        """Called when something on the entry changes"""
        self._last_change_time = time.time()
        self.emit('content-changed')

    def read(self):
        text = self.child.get_text()
        self._validate_data(text)
        return self._validate_data(text)

    def do_validate(self, data):
        """ComboBoxEntry has a validate default handler that check if the
        text of the entry is an item of the list"""
        items = self.get_model_items()

        if data is None or not data.strip():
            return

        if data not in items.keys():
            if self._list_writable:
                error = ValidationError("Entered value not in list. "
                                        "To add an item, type "
                                        "the value and press enter")
            else:
                error = ValidationError("Entered value not in list")
            return error
    
    def update(self, data):
        # first, trigger some basic validation
        WidgetProxy.Mixin.update(self, data)
        if data is ValueUnset or data is None:
            self.child.set_text("")
            self.draw_mandatory_icon_if_needed()
        else:
            self.select_item_by_data(data)

    def prefill(self, itemdata, sort=False, clear_entry=False):
        ComboProxyMixin.prefill(self, itemdata, sort)
        if clear_entry:
            self.child.set_text("")

        # setup the autocompletion
        auto = gtk.EntryCompletion()
        auto.set_model(self.get_model())
        auto.set_text_column(0)
        self.child.set_completion(auto)
        
    def clear(self):
        """Removes all items from list and erases entry"""
        ComboProxyMixin.clear(self)
        self.child.set_text("")
        
    
gobject.type_register(ComboBoxEntry)



