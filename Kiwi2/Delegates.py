#!/usr/bin/env python
#
# Kiwi: a Framework and Enhanced Widgets for Python
#
# Copyright (C) 2002, 2003 Async Open Source
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

"""Defines the Delegate classes that are included in the Kiwi Framework."""

from Kiwi.Views import SlaveView, GladeView, GladeSlaveView, BaseView
from Controllers import BaseController

class SlaveDelegate(SlaveView, BaseController):
    """A class that combines view and controller functionality into a
single package. It does not possess a top-level window, but is instead
intended to be plugged in to a View or Delegate using attach_slave()."""
    def __init__(self, toplevel=None, widgets=[]):
        """Create new SlaveDelegate. toplevel is the toplevel widget,
defaults to the value of the class' toplevel attribute, and if not
present, raises AttributeError."""
        SlaveView.__init__(self, toplevel, widgets)
        BaseController.__init__(self, view=self)

class GladeSlaveDelegate(GladeSlaveView, BaseController):
    """A class that combines a controller and a GladeSlaveView. It is
intended to be plugged into a View or Delegate using attach_slave()."""
    def __init__(self, gladefile=None, container_name=None, widgets=[]):
        """Creates a new GladeSlaveDelegate. gladefile is the name of
the Glade XML file, and container_name is the name of the toplevel
GtkWindow that holds the slave."""
        GladeSlaveView.__init__(self, gladefile, container_name, widgets)
        BaseController.__init__(self, view=self)

class Delegate(BaseView, BaseController):
    """A class that combines view and controller functionality into a
single package. The Delegate class possesses a top-level window."""
    def __init__(self, toplevel=None, delete_handler=None, widgets=[]):
        """Creates a new Delegate. For parameters , see
BaseView.__init__"""
        BaseView.__init__(self, toplevel, delete_handler, widgets)
        BaseController.__init__(self, view=self)

class GladeDelegate(GladeView, BaseController):
    """A Delegate that uses a Glade file to specify its UI."""
    def __init__(self, gladefile=None, toplevel_name=None, 
                 delete_handler=None, widgets=[]):
        """Creates a new GladeDelegate. For parameters, see
GladeView.__init__"""
        GladeView.__init__(self, gladefile, toplevel_name, delete_handler, 
                           widgets)
        BaseController.__init__(self, view=self)

