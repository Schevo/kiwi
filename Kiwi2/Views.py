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
#            Jon Nelson <jnelson@securepipe.com>
#

"""
Defines the View classes that are included in the Kiwi Framework, which
are the base of Delegates and Proxies.
"""

from Kiwi2 import _warn
from Kiwi2.initgtk import gtk, _non_interactive
from Kiwi2.AbstractViews import AbstractView, AbstractGladeView

#
#
#

class SlaveView(AbstractView):
    """A view for a widget hierarchy without a Window or Dialog
enclosing it. Instead, the SlaveView is intended to be attached to
another View (or directly to a Window). The toplevel widget is
offered through get_toplevel().

SlaveView holds two public variables:
    - controller: which is the controller associated to this view. For
      delegates that subclass slaveview, this corresponds to self.
    - widgets: a list of widget names. This list describes which widgets
      are to be converted to kiwi widgets, and for GladeViews, it
      determines which widgets will be attached to the view as instance
      variables. 

      For proxies, names prefixed with a colon (:) are considered to be
      widgets associated to model attributes (with the same names, or
      with accessors with the appropriate names). See VirtualProxy for
      more details."""
    def __init__(self, toplevel=None, widgets=None):
        """
Creates a new SlaveView. Parameters:
    - toplevel: the toplevel widget for this view.
"""
        AbstractView.__init__(self, toplevel, widgets)
        
        # LLL This hase changed in GTK+ 2.x
        #self._accel_groups = gtk_accel_groups_from_object(self.toplevel._o)

#
#
#

class GladeSlaveView(AbstractGladeView, AbstractView):
    """A SlaveView that is built upon a Glade file. The contents you
want to be used as a slave should be placed inside a placeholder
Window. The placeholder will be destroyed and self.toplevel 
will be assigned to the placeholder's original contents."""
    container_name = None
    def __init__(self, gladefile=None, container_name=None, widgets=None):
        """
        Creates a new GladeSlaveView.

        - gladefile: the name of the glade filename; it will be searched for
          in the gladepath (GLADEPATH). If not supplied, the name of the
          gladefile will be used.

        - container_name: the name of the Window enclosing the slave. If
          not supplied, the same name as the gladefile name will be used.

        - widgets: the widgets list, which can also be assigned as a class
          attribute.

        The container_name parameter should indicate the name of this
        toplevel window. The slave will be removed from this placeholder, and
        self.toplevel will be assigned to it. The placeholder Window's destroy()
        method is called.
        """

        if getattr(self, "toplevel", None):
            _warn("GladeSlaveView does not use the `toplevel' attribute; "
                  "instead, provide a container_name")

        AbstractGladeView.__init__(self, gladefile, widgets)

        container_name = container_name or self.container_name or self.gladename

        # GladeSlaveViews need to come inside a toplevel window, so we
        # pull our slave out from it, grab its groups and murder it later.
        shell = self.tree.get_widget(container_name)
        if not isinstance(shell, gtk.Window):
            raise TypeError,  "Container %s should be a Window, found %s" \
                               % (container_name, shell)

        # LLL changed in GTK+ 2.x
        #self._accel_groups = gtk_accel_groups_from_object(shell.get_toplevel()._o)
        self.toplevel = shell.get_children()[0]

        shell.remove(self.toplevel)
        shell.destroy()

        AbstractView.__init__(self, self.toplevel, widgets)

#
#
#
        
class BaseView(AbstractView):
    """A view with a toplevel window."""
    win = None
    def __init__(self, toplevel=None, delete_handler=None, widgets=None):
        """
        toplevel is the widget to be set as `toplevel' (and which will
        be aliased as `win'); delete_handler allows setting a function
        to be called when this view's window is deleted."""
        self.toplevel = toplevel or self.win or self.toplevel 
        AbstractView.__init__(self, toplevel, widgets)
        # Make sure self.win is set correctly
        self.win = self.toplevel

        if not isinstance(self.toplevel, gtk.Window):
            raise TypeError, ("toplevel widget must be a Window "
                              "(or inherit from it),\nfound `%s' %s" 
                              % (toplevel, self.toplevel))
        # Create method alias
        self.get_win = self.get_toplevel

        if delete_handler:
            id = self.win.connect("delete_event", delete_handler)
            if not id:
                raise ValueError, \
                    "Invalid delete handler provided: %s" % delete_handler

    #
    # Hook for keypress handling
    #

    def _setup_keypress_handler(self, keypress_handler):
        self.connect_after("key_press_event", keypress_handler)

    #
    # Proxying for self.win
    #

    def connect(self, *args):
        """
        connect(signal, handler, arguments)

        Connects a signal from the view's window to the handler
        specified."""
        return apply(self.win.connect, args)
    
    def connect_after(self, *args):
        """
        connect_after(signal, handler, arguments)

        Connects (using connect_after) a signal from the view's window to the
        handler specified."""
        return apply(self.win.connect_after, args)

    def set_transient_for(self, view):
        """
        Makes the view a transient for another view; this is commonly done for
        dialogs, so the dialog window is managed differently than a top-level
        one."""
        if hasattr(view, "win"):
            self.win.set_transient_for(view.win)
        # In certain cases, it is more convenient to send in a window;
        # for instance, in a deep slaveview hierarchy, getting the
        # top view is difficult. We used to print a warning here, I
        # removed it for convenience; we might want to put it back when
        # http://bugs.async.com.br/show_bug.cgi?id=682 is fixed
        elif isinstance(view, gtk.Window):
            self.win.set_transient_for(view)
        else:
            raise TypeError, ("Parameter to set_transient_for should "
                              "be View (found %s)" % view)

    def set_title(self, title):
        """Sets the view's window title"""
        self.win.set_title(title)

    #
    # Focus handling
    #

    def get_focus_widget(self):
        """Returns the currently focused widget in the window"""
        if not hasattr(self.win, "focus_widget"):
            raise AttributeError, "You need pygtk-0.6.8 or later"
        return self.win.focus_widget

    def check_focus(self, complain=1):
        """
        Tests the focus in the window and prints a warning if no
        widget is focused.

            - complain: warn if version of pygtk is too old
        """
        if hasattr(self.win, "focus_widget"):
            focus = self.win.focus_widget
            if focus:
                return
            values = self.__dict__.values()
            interactive = None
            # Check if any of the widgets is interactive
            for v in values:
                if (isinstance(v, gtk.Widget) and not
                    isinstance(v, _non_interactive)):
                    interactive = v
            if interactive:
                _warn("no widget is focused in view %s but you have an "
                      "interactive widget in it: %s""" % (self, interactive))
        elif complain:
            _warn("check_focus is not supported for versions of "
                  "PyGTK before 0.6.8, please upgrade")

    #
    # Window show/hide and mainloop manipulation
    #

    def hide(self, *args):
        """Hide the view's  window"""
        self.win.hide()

    def show_all(self, *args):
        self.win.show_all()
        # Uniconize window if minimized
        gdkwin = self.win.window
        if gdkwin:
            gdkwin.show()

    def show(self, *args):
        """Show the view's window"""
        self.win.show()
        # Uniconize window if minimized
        gdkwin = self.win.window
        if gdkwin:
            gdkwin.show()

    def show_and_loop(self, parent=None):
        """
        Runs show() and runs the GTK+ event loop. If the parent argument
        is supplied and is a valid view, this view is set as a transient
        for the parent view"""
        self.show()
        self.check_focus(complain=0)
        return self._loop(parent)

    def show_all_and_loop(self, parent=None):
        """
        Runs show_all() and runs the GTK+ event loop. If the parent
        argument is supplied and is a valid view, this view is set as a
        transient for the parent view"""
        self.show_all()
        self.check_focus(complain=0)
        return self._loop(parent)

    def _loop(self, parent):
        # XXX: take care of modality?
        if parent:
            self.set_transient_for(parent)
        gtk.main()
        return getattr(self, "retval", None)

    def hide_and_quit(self, *args):
        """
        Hides the current window and breaks the GTK+ event loop. Its
        method signature allows it to be used as a signal handler."""
        self.win.hide()
        gtk.main_quit()

#
#
#

class GladeView(AbstractGladeView, BaseView):
    """
    A complete view based on a Glade file, and which contains a
    top-level window."""
    def __init__(self, gladefile=None, toplevel_name=None, 
                 delete_handler=None, widgets=None):
        """
        Creates a new GladeView. Parameters:

            - gladefile: name of the glade file we are loading. If the
              file name is not suffixed by '.glade', append it. If not
              set, use the 'glade' attribute of the instance.

            - toplevel_name: *name* of the top-level widget that will be
              considered the win member. Should correspond to a Window.
              If not set, uses the name of the gladefile (minus
              '.glade')

              Note that it is the *name* of the widget, not the widget itself: this is
              different from Base/SlaveView!

            - delete_handler: function to be called as a callback when
              delete is called on the toplevel. 

            - widgets: a list of strings that define widget names to get
              from the glade file and attach to the view as instance
              variables
        """
        AbstractGladeView.__init__(self, gladefile, widgets)
        
        name = toplevel_name or self.gladename
        self.win = self.tree.get_widget(name)
        self._accel_groups = []

        if not self.win:
            msg = "%s must contain a widget called %s"
            raise SyntaxError, msg % (self.gladefile, name)
        if self.win.flags() & gtk.VISIBLE:
            _warn("widget %s (%s) is visible; that's probably "
                  "wrong" % (self.win, name))
    
        try:
            # BaseView wants self.win defined
            BaseView.__init__(self, delete_handler=delete_handler)
        except KeyError: 
            raise KeyError, ("Some widgets were defined in self.widgets " 
                             "but not found in the glade tree (see previous "
                             "messenges to see which ones).")

    def show_all(self, *args):
        """Don't use show_all on a GladeView; use show()"""
        raise AssertionError, ("You don't want to call show_all on a "
                               "GladeView. Use show() instead.")
    
    def show_all_and_loop(self, *args):
        """Don't use show_all_and_loop on a GladeView; use show_and_loop()"""
        raise AssertionError, ("You don't want to call show_all_and_loop "
                               "on GladeView.  Use show_and_loop() instead.")
