#!/usr/bin/env python
#
# Kiwi: a Framework and Enhanced Widgets for Python
#
# Copyright (C) 2001-2004 Async Open Source
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

"""XXX"""

import string
from types import ListType, TupleType

class BaseController:
    """
    A generic controller that can be attached to any View

    BaseController defines one public variable: 
    
        - view: corresponds to a the associated View instance, which
          holds the UI implementation itself (widgets, layout, etc.)
    """
    view = None
    def __init__(self, view=None, keyactions=None):
        """
        Creates a new controller, and attaches itself to a view. The
        constructor triggers a view.set_constructor(self) call, so the
        view is also attached to it. The arguments are identical to the
        view and keyactions class variables.

        - view: the correspondent view for the controller
        - keyactions: a mapping from GDK key symbol (GDK.A, etc.) to a
          method. The method will be called when any relevant keypress is
          generated for that view. The handler definition should look like:

              def my_A_handler(self, widget, event, args):
        """

        if not view and not self.view:
            raise AssertionError, \
                "Need a view to create controller, found None" 
        else:
            self.set_view(view)

        # Copy just to be on the safe side, avoiding problems with
        # mutable class variables
        self.__keyactions = keyactions or {}
                
        # Handle signals set in glade
        self.view._attach_callbacks(self)

        # Call finalization hook
        self.view.on_startup()

    #
    # Hooks
    #

    def on_key_press(self, widget, event, *args):
        """
        The keypress handler, which dispatches keypresses to the
        functions mapped to in self.keyactions"""
        this_key = event.keyval
        if self.__keyactions.has_key(this_key):
            return self.__keyactions[this_key](widget, event, args)
        return None

    #
    # Accessors
    #

    def get_parent(self):
        """parent: the correspondent parent for the controller"""
        return self.parent

    def set_parent(self, parent):
        """parent: the correspondent parent for the controller"""
        self.parent = parent
    
    def get_view(self):
        """view: the correspondent view for the controller"""
        return self.view

    def set_view(self, view):
        """view: the correspondent view for the controller"""
        if self.view:
            msg = "This controller already has a view: %s"
            raise AssertionError, msg % self.view
        self.view = view
        view.set_controller(self)
    
    def set_keyactions(self, keyactions):
        """
        Sets the keyactions mapping. See the constructor
        documentation for a description of it."""
        self.__keyactions = keyactions

    def update_keyactions(self, new_actions):
        """
        XXX
        """
        self.__keyactions.update(new_actions)

    #
    #
    #

    def _get_all_methods(self, klass=None):
        klass = klass or self.__class__
        # Very poor simulation of inheritance, but WFM(tm)
        classes=[ klass ] 
        # Collect bases for class, using a pretty evil recursion
        for klass in classes:
            map(classes.append, klass.__bases__)
        # Order bases so that the class itself is the last one referred to
        # in the loop. This guarantees that the inheritance ordering for the
        # methods is preserved.
        classes.reverse()
        methods = {}
        for c in classes:
            for name in c.__dict__.keys():
                # Need to use getattr() to ensure we get bound methods
                methods[name] = getattr(self, name)
        return methods

