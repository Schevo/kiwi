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

class ValueUnset:
    """To differentiate from places where None is a valid default. Used
    mainly in the Kiwi Proxy"""
    pass

# this functions will live here until we find a better place
def str2bool(value, default_value=True):
    if value.upper() in ('TRUE', '1'):
        return True
    elif value.upper() in ('FALSE', '0'):
        return False
    else:
        return default_value

def str2enum(value_name, enum_class):
    for value, enum in enum_class.__enum_values__.items():
        if value_name in (enum.value_name, enum.value_nick):
            return enum

def str2type(value, default_type=str):
    type_map = {'str': str, 'int': int, 'float': float}
    return type_map.get(value, default_type)

from Kiwi2.initgtk import gtk
#from Kiwi2.WidgetProxies import Entry, Text, CheckButton, OptionMenu
#from Kiwi2.WidgetProxies.Base import ConversionError

from Kiwi2.version import version
kiwi_version = version

from Kiwi2.List import List

standard_widgets = {
    #gtk.Entry        : Entry.EntryProxy,
    #gtk.Combo        : Entry.ComboProxy,
    #gtk.Label        : Entry.LabelProxy,
    #gtk.SpinButton   : Entry.SpinButtonProxy,

    #gtk.ToggleButton : CheckButton.ToggleButtonProxy,
    #gtk.CheckButton  : CheckButton.CheckButtonProxy,

    #gtk.Text         : Text.TextProxy,
    #gtk.OptionMenu   : OptionMenu.OptionMenuProxy,
}

# Kiwi Combo, GtkRadioButton are non-standard and are handled specially
# inside AbstractProxy

from sys import stderr

def _warn(msg):
    stderr.write("Kiwi warning: "+msg+"\n")

gladepath = []
