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

from Kiwi2.initgtk import gtk, gobject
from Kiwi2.Widgets import WidgetProxy
from Kiwi2.utils import gsignal, gproperty
from Kiwi2 import ValueUnset

class SpinButton(gtk.SpinButton, WidgetProxy.MixinSupportValidation):
    WidgetProxy.implementsIProxy()
    WidgetProxy.implementsIMandatoryProxy()

    gsignal('value-changed', 'override')
    # mandatory widgets need to have this signal connected
    gsignal('expose-event', 'override')
    
    
    def __init__(self):
        # since the default data_type is str we need to set it to int 
        # or float for spinbuttons
        WidgetProxy.MixinSupportValidation.__init__(self, data_type=int)
        gtk.SpinButton.__init__(self)
        self.connect('output', self._on_spinbutton__output)
        
        # this attribute stores the info on where to draw icons and paint
        # the background
        self._widget_to_draw = self
        
        # due to changes on pygtk 2.6 we have to make some ajustments here
        if gtk.pygtk_version < (2,6):
            self.do_expose_event = self.chain
        
    def _on_spinbutton__output(self, *args):
        self.emit('content-changed')
        
    def set_data_type(self, data_type):
        """Overriden from super class. Since spinbuttons should
        only accept float or int numbers we need to make a special
        treatment.
        """
        old_datatype = self._data_type
        WidgetProxy.MixinSupportValidation.set_data_type(self, data_type)
        if self._data_type not in (int, float):
            self._data_type = old_datatype
            raise TypeError("SpinButtons only accept integer or float values")
        
    def do_value_changed(self):

        self._last_change_time = time.time()        
        
        if len(self.get_text()) == 0 and self._mandatory:
            self._draw_mandatory_icon = True
        else:
            self._draw_mandatory_icon = False
            
        self.emit('content-changed')
        self.chain()

    def read(self):
        text = self.get_value()
        data = self._validate_data(self.type2str(text))

        return data

    def update(self, data):
        WidgetProxy.MixinSupportValidation.update(self, data)
        
        if data is not ValueUnset and data is not None:
            self.set_value(data)
        else:
            self.set_text("")

    def do_expose_event(self, event):
        """Expose-event signal are triggered when a redraw of the widget
        needs to be done.
        
        Draws information and mandatory icons when necessary
        """        
        result = gtk.SpinButton.do_expose_event(self, event)
        
        # this attribute stores the info on where to draw icons and paint
        # the background
        # it's been defined here because it's when we have gdk window available
        self._gdkwindow_to_draw = self.window
        
        self._draw_icon()
        
        return result
    
gobject.type_register(SpinButton)
