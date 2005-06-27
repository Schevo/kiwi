#
# Kiwi: a Framework and Enhanced Widgets for Python
#
# Copyright (C) 2001-2005 Async Open Source
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
#

"""
This module initializes GTK+ and sets up any globals necessary

The reason to initialize GTK+ in a separate module and not in the __init__.py
file is that some parts of the Kiwi Framework should be usable without
any graphics involved.
"""

import sys

# Before trying to import pygtk, check if gtk is already imported
if not ('gtk._gtk' in sys.modules or
        'gobject' in sys.modules):
    try:
        import pygtk
        pygtk.require('2.0')
    except ImportError:
        raise ImportError("Couldn't import required package PyGTK+ 2.x")

import gtk
import gobject

glib_version = gobject.glib_version
from gtk import gtk_version
from gtk import pygtk_version
from gtk import mainquit, main

_non_interactive = [
    gtk.Label, 
    gtk.Alignment,
    gtk.AccelLabel,
    gtk.Arrow,
    gtk.EventBox,
    gtk.Fixed,
    gtk.Frame,
    gtk.HBox,
    gtk.HButtonBox,
    gtk.HPaned,
    gtk.HSeparator,
    gtk.Layout,
    gtk.Progress,
    gtk.ProgressBar,
    gtk.ScrolledWindow,
    gtk.Table,
    gtk.VBox,
    gtk.VButtonBox,
    gtk.VPaned,
    gtk.VSeparator,
    gtk.Window, 
]

try: 
    import gtk.glade
    _non_interactive.append(gtk.glade.XML)
except ImportError:
    gtk.glade = None

_non_interactive = tuple(_non_interactive)


# one big difference between Kiwi1 and kiwi is
# that we are just using one gtk mainloop

def quit_if_last(*args):
    windows = [toplevel
               for toplevel in gtk.window_list_toplevels()
                   if toplevel.get_property('type') == gtk.WINDOW_TOPLEVEL]
    if len(windows) == 1:
        gtk.main_quit()
