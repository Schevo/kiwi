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

from Kiwi2.initgtk import gtk, gobject
from Kiwi2.Widgets.WidgetProxy import WidgetProxyMixin, implementsIProxy
from Kiwi2.utils import gsignal

(COL_COMBO_LABEL,
 COL_COMBO_DATA) = range(2)

class ComboProxyMixin(WidgetProxyMixin):
    """Our combos always have one model with two columns, one for the string
    that is displayed and one for the object it cames from.
    """
    def __init__(self):
        """Call this constructor after the Combo one"""
        WidgetProxyMixin.__init__(self)

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
            raise KeyError("No item correspond to label %s" % label)
    
    def select_item_by_data(self, data):
        model = self.get_model()
        for row in model:
            if row[COL_COMBO_DATA] == data:
                self.set_active_iter(row.iter)
                break
        else:
            raise KeyError("No item correspond to data %r" % data)

    def get_selected_label(self):
        model = self.get_model()
        iter = self.get_active_iter()
        if iter:
            return model.get(iter, COL_COMBO_LABEL)[0]
            
    def get_selected_data(self):
        model = self.get_model()
        iter = self.get_active_iter()
        if iter:
            return model.get(iter, COL_COMBO_DATA)[0]

class ComboBox(gtk.ComboBox, ComboProxyMixin):
    implementsIProxy()
    gsignal('changed', 'override')
    
    def __init__(self):
        gtk.ComboBox.__init__(self)
        ComboProxyMixin.__init__(self)

        renderer = gtk.CellRendererText()
        self.pack_start(renderer)
        self.add_attribute(renderer, 'text', 0)

    def do_changed(self):
        self.emit('content-changed')
        self.chain()
        
    def read(self):
        active_iter = self.get_active_iter()
        if active_iter is not None:
            text = self.get_model().get_value(active_iter, 0)
            return self.str2type(text)

    def update(self, data):
        # first, trigger some basic validation
        WidgetProxyMixin.update(self, data)
        model = self.get_model()
        it = model.get_iter_first()
        while it:
            v = model.get_value(it, 0)
            if v == data:
                self.set_active_iter(it)
                break
            it = model.iter_next(it)

    def prefill(self, itemdata, sort=False):
        super(ComboBox, self).prefill(itemdata, sort)

        # we always have something selected, by default the first item
        self.set_active(0)
        self.emit('content-changed')

    def clear(self):
        ComboProxyMixin.clear(self)
        
gobject.type_register(ComboBox)

class ComboBoxEntry(gtk.ComboBoxEntry, ComboProxyMixin):
    implementsIProxy()
    
    def __init__(self):
        gtk.ComboBox.__init__(self)
        ComboProxyMixin.__init__(self)

        self.set_text_column(0)
        self.child.connect('changed', self._on_entry__changed)

    def _on_entry__changed(self, entry):
        self.emit('content-changed')
        
    def read(self):
        return self.str2type(self.child.get_text())

    def update(self, data):
        # first, trigger some basic validation
        WidgetProxyMixin.update(self, data)
        self.child.set_text(self.type2str(data))

    def prefill(self, itemdata, sort=False, clear_entry=False):
        super(ComboBoxEntry, self).prefill(itemdata, sort)
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
