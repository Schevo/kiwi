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
XXX
"""

import os, string, re, sys

from Kiwi2 import _warn, gladepath
from Kiwi2.initgtk import _non_interactive, gtk

#
# Gladepath handling
#

def find_in_gladepath(filename):
    """Looks in gladepath for the file specified"""

    # check to see if gladepath is a list or tuple
    if not isinstance(gladepath, (tuple, list)):
        msg ="gladepath should be a list or tuple, found %s"
        raise ValueError, msg % type(gladepath)

    if os.sep in filename or not gladepath:
        if os.path.isfile(filename):
            return filename
        else:
            raise IOError, "%s not found" % filename

    for path in gladepath:
        # append slash to dirname
        if not path:
            continue
        # if absolute path
        fname = os.path.join(path, filename)
        if os.path.isfile(fname):
            return fname

    raise IOError, \
    """%s not found in path %s.  You probably need to
Kiwi.set_gladepath() correctly""" % ( filename, gladepath )

#
# Signal brokers
#

class SignalBroker:
    def __init__(self, view, controller):
        methods = controller._get_all_methods()
        self._do_connections(view, methods)

    def _do_connections(self, view, methods):
        """This method allows subclasses to add more connection mechanism"""
        self._autoconnect_by_method_name(view, methods)
        
    def _autoconnect_by_method_name(self, view, methods):
        """
        Offers autoconnection of widget signals based on function names.
        You simply need to define your controller method in the format::

            def on_widget_name__signal_name(self, widget, *args):

        In other words, start the method by "on_", followed by the
        widget name, followed by two underscores ("__"), followed by the
        signal name. Note: If more than one double underscore sequences
        are in the string, the last one is assumed to separate the
        signal name.
        """
        self._autoconnected = {}
        for fname in methods.keys():
            # `on_x__y' has 7 chars and is the smallest possible handler
            # (though illegal, of course, since the signal name x is bogus)
            if len(fname) < 7:
                continue
            if fname[:3] == "on_":
                after = 0
            elif fname[:6] == "after_":
                after = 1
            else:
                continue
            # cut out `on_' or `after'
            f = string.split(fname, "_", 1)
            if len(f) < 2:
                continue
            f = f[1]
            # separate widget from signal; for instance: 
            # "on_foo_bar__widget__clicked()" -> "foo_bar", "widget", "clicked"
            f = string.split(f, "__")
            if len(f) < 2:
                continue
            # signal is the last element
            signal = f[-1]
            # widget name is everything up to the last __
            # "foo_bar", "widget" -> "foo_bar__widget"
            w_name = string.join(f[:-1], "__")
            if not w_name:
                continue
            widget = getattr(view, w_name, None)
            if not widget:
                raise AttributeError, \
                    "couldn't find widget %s in %s" % (w_name, view)
            if not isinstance(widget, gtk.Widget):
                raise AttributeError, \
                    "%s (%s) is not a widget and can't be connected to" \
                        % (w_name, widget)
            # Must use getattr; using the class method ends up with it
            # being called unbound and lacking, thus, "self".
            if after:
                id = widget.connect_after(signal, methods[fname])
            else:
                id = widget.connect(signal, methods[fname])
            if not id:
                raise AttributeError, "Widget %s doesn't provide a signal %s" \
                                       % (widget.__class__, signal)
            if not self._autoconnected.has_key(widget):
                self._autoconnected[widget] = []
            self._autoconnected[widget].append(id)

class GladeSignalBroker(SignalBroker):
    def __init__(self, view, controller):
        SignalBroker.__init__(self, view, controller)

    def _do_connections(self, view, methods):
        super(GladeSignalBroker, self)._do_connections(view, methods)
        self._connect_glade_signals(view, methods)
        
    def _connect_glade_signals(self, view, methods):
        # mainly because the two classes cannot have a common base
        # class. studying the class layout carefully or using
        # composition may be necessary.

        # called by framework.basecontroller. takes a controller, and
        # creates the dictionary to attach to the signals in the tree.
        if not methods:
            raise assertionerror, "controller must be provided"

        dict = {}
        for name, method in methods.items():
            if callable(method):
                dict[name] = method
        view.tree.signal_autoconnect(dict)

        self._autoconnect_by_method_name(view, methods)
        
#
# Abstract Classes, used by other Views
#

class AbstractView:
    """
    Base class for all View classes. Defines the essential class
    attributes (controller, toplevel, widgets) and handles
    initialization of toplevel and widgets.  Once
    AbstractView.__init__() has been called, you can be sure
    self.toplevel and self.widgets are sane and processed.

    When a controller is associated with a View (the view should be
    passed in to its constructor) it will try and call a hook in the
    View called _attach_callbacks. See AbstractGladeView for an example
    of this method.
    """
    controller = None
    toplevel = None
    widgets = None
    _initted = False

    def __init__(self, toplevel, widgets=None):
        """
        Creates a new AbstractView. Sets up self.toplevel and
        self.widgets, checks for reserved names, and converts the
        widgets defined in the _widget_map to Kiwi widgets.
        """
        self.toplevel = toplevel or self.toplevel
        self.widgets = widgets or self.widgets or []
        self._initted = True
        
        if not self.toplevel:
            raise TypeError, \
                ("A View requires an instance variable called toplevel "
                 "that specifies the toplevel widget in it")

        for reserved in ["win", "widgets", "toplevel", "gladefile",
                         "gladename", "tree", "model", "controller"]:
            # XXX: take into account widget constructor?
            if reserved in self.widgets:
                raise AttributeError, ("The widgets list for %s contains "
                                       "a widget named `%s', which is "
                                       "a reserved. name""" % (self, reserved))

        # Convert widgets to their Kiwi counterparts
        self._convert_widgets()

    #
    # Hooks
    #

    def on_attach(self, parent):
        """
        Hook function called when attach_slave is performed on slave
        views."""
        pass

    def on_startup(self):
        """
        This is a virtual method that can be customized by classes that
        want to perform additional initalization after a controller has
        been set for it.  If you need this, add this method to your View
        subclass and BaseController will call it when the controller is
        set to the proxy."""
        pass

    #
    # Accessors
    #

    def get_toplevel(self):
        """Returns the toplevel widget in the view"""
        return self.toplevel

    def get_widget(self, name):
        """Retrieves the named widget from the View"""
        name = string.replace(name,'.','_')
        widget = getattr(self, name, None)
        if not widget:
            raise AttributeError, \
                "Widget %s not found in view %s" % (name, self)
        if not isinstance(widget, gtk.Widget):
            raise TypeError, \
                "%s in view %s is not a Widget" % (name, self)
        return widget

    def set_controller(self, controller):
        """
        Sets the view's controller, checking to see if one has already
        been set before."""
        # Only one controller per view, please
        if self.controller:
            raise AssertionError, \
                "This view already has a controller: %s" % self.controller
        self.controller = controller

    #
    # GTK+ proxies and convenience functions
    #

    def show_all(self, *args):
        """Shows all widgets attached to the toplevel widget"""
        self.toplevel.show_all()

    def focus_toplevel(self):
        """Focuses the toplevel widget in the view"""
        # XXX: warn if there is no GdkWindow
        if self.toplevel and self.toplevel.window is not None:
            self.toplevel.grab_focus()

    def focus_topmost(self, widgets=None):
        """
        Looks through widgets specified (if no widgets are specified,
        look through all widgets attached to the view and sets focus to
        the widget that is rendered in the position closest to the view
        window's top and left

            - widgets: a list of widget names to be searched through
        """
        widget = self.get_topmost_widget(widgets, can_focus=1)
        if widget: 
            widget.grab_focus()
        # So it can be idle_added safely
        return False

    def get_topmost_widget(self, widgets=None, can_focus=0):
        """
        A real hack; returns the widget that is most to the left and
        top of the window. 

            - widgets: a list of widget names.  If widgets is supplied,
              it only checks in the widgets in the list; otherwise, it
              looks at the widgets named in self.widgets, or, if
              self.widgets is None, looks through all widgets attached
              to the view.

            - can_focus: boolean, if set only searches through widget that can focus
        """
        # XXX: recurse through containers from toplevel widget, better
        # idea and will work.
        widgets = widgets or self.widgets or self.__dict__.keys()
        top_widget = None
        for widget_name in widgets:
            widget = getattr(self, widget_name)
            if not isinstance(widget, gtk.Widget):
                continue
            if not widget.flags() & gtk.REALIZED:
                # If widget isn't realized but we have a toplevel
                # window, it's safe to realize it. If this check isn't
                # performed, we get a crash as per
                # http://bugzilla.gnome.org/show_bug.cgi?id=107872
                if isinstance(widget.get_toplevel(), gtk.Window):
                    widget.realize()
                else:
                    _warn("get_topmost_widget: widget %s was unrealized"
                          % widget_name)
                    continue
            if can_focus:
                # Combos don't focus, but their entries do
                if isinstance(widget, gtk.Combo):
                    widget = widget.entry
                if not widget.flags() & gtk.CAN_FOCUS or \
                    isinstance(widget, (gtk.Label, gtk.HSeparator,
                                        gtk.VSeparator, gtk.Window)):
                    continue
            allocation = widget.get_allocation()
            if top_widget:
                top_allocation = top_widget.get_allocation()
                if top_allocation[0] + top_allocation[1] > \
                   allocation[0] + allocation[1]:
                    top_widget = widget
            else:
                top_widget = widget
        return top_widget

    #
    # Color control
    #
    def set_background(self, widget, color, state=gtk.STATE_NORMAL):
        """sets the background color for a widget"""
        widget.modify_bg(state, gtk.gdk.color_parse(color))

    def set_foreground(self, widget, color, state=gtk.STATE_NORMAL):
        """sets the foreground color for a widget"""
        widget.modify_fg(state, self.gdk.color_parse(color))

    def set_color(self, widget, color, attr_name, state=gtk.STATE_NORMAL):
        """
        Generic color setter.
            - widget: which widget to change the style color for
            - color: a color specified as a name or hex triplet
            - attr_name: a string with the member name of the style object we should
              change (normally "fg" or "bg")
            - state: the style state for which to change color, defaults to
              gtk.STATE_NORMAL
        """
        map = widget.get_colormap()
        s = widget.get_style()
        s = s.copy()
        attr = getattr(s, attr_name)
        attr[state] = map.alloc_color(color)
        widget.set_style(s)

    #
    # Widget registration and substitution
    #

    def register_widget(self, widgets, klass):
        """
        Allows a new widget class to be overridden for a single widget
        or a list of widgets. Note: call this method *BEFORE* calling
        the constructor of *View or it won't do what you want. Yes, you
        must subclass *View if you would like to register custom
        widgets.

            - widgets: a widget name (string) or a list of widget names
            - klass: a class to which the specified widgets will be
              converted.  Note that the klass *should* inherit from its
              gtk counterpart, and that it must provide a _initialize()
              method (all Kiwi widgets do).

        If you would like to change a widget class *globally*, use
        Views.register_widget.
        """
        if self._initted:
            raise TypeError, \
                "register_widget must be called before superclass constructor"
        # Use a new dictionary if the current one is empty
        self._custom_widgets = self._custom_widgets or {}
        if isinstance(widgets, basestring):
            self._custom_widgets[widgets] = klass
        elif isinstance(widgets, (list, tuple)):
            for w in widgets:
                self._custom_widgets[w] = klass
        else:
            raise TypeError, \
            "widgets should be string or sequence, found %s" % type(widgets)

    #
    # Callback handling
    #

    def _attach_callbacks(self, controller):
        self.__broker = SignalBroker(self, controller)
        self._setup_keypress_handler(controller.on_key_press)

    def _setup_keypress_handler(self, keypress_handler):
        # Only useful in BaseView and derived classes
        # XXX: support slaveview correctly
        _warn("Tried to setup a keypress handler for %s "
              "but no toplevel window exists to attach to" % self)
    
    #
    # Signal connection
    #

    def connect_multiple(self, widgets, signal, handler, after=0):
        """
        Connect the same handler to the specified signal for a number of
        widgets.
            - widgets: a list of GtkWidgets
            - signal: a string specifying the signals
            - handler: a callback method
            - after: a boolean; if TRUE, we use connect_after(), otherwise, connect()
        """
        if not isinstance(widgets, (list, tuple)):
            raise TypeError, "widgets must be a list, found %s" % widgets
        for widget in widgets:
            if not isinstance(widget, gtk.Widget):
                raise TypeError, \
                "Only Gtk widgets may be passed in list, found\n%s" % widget
            if after:
                widget.connect_after(signal, handler)
            else:
                widget.connect(signal, handler)

    def disconnect_autoconnected(self):
        """
        Disconnect handlers previously connected with 
        autoconnect_signals()"""
        for widget, signals in self._autoconnected.items():
            for signal in signals:
                widget.disconnect(signal)

    def _convert_widgets(self):
        """
        Convert GTK+ widgets in the self.widgets list to Kiwi widgets
        based on _widget_map. You can change which widgets we convert to
        by using the module function Views.register_widget()."""
        global sane_editables

        if not self.widgets:
            return

        for w in self.widgets:
            widget = getattr(self, w, None)
            if not widget:
                raise KeyError, \
                    "Widget %s in self.widgets but not a view attribute" % w

#             # Sanitize, first thing, if sane editables are enabled
#             if sane_editables:
#                 if (isinstance(widget, gtk.Entry) or
#                     isinstance(widget, gtk.SpinButton)):
#                     self._sanitize_entry(widget)
# 
#                 if isinstance(widget, gtk.Combo):
#                     self._sanitize_entry(widget.entry)
# 
#                 if isinstance(widget, gtk.Text):
#                     self._sanitize_text(widget)
# 
#             klass = widget.__class__
#             if self._custom_widgets.has_key(w):
#                 klass = self._custom_widgets[w]
#             elif _widget_map.has_key(klass):
#                 klass = _widget_map[klass]
#             else:
#                 # This widget doesn't have a custom Kiwi widget
#                 continue
#             
#             if not hasattr(klass, "_initialize"):
#                 raise TypeError, \
#                 "class %s should offer an _initialize() method" % klass
# 
#             # One day this may break (in Python2.3?)
#             widget.__class__ = klass
#         
#             # Each class should provide an _initialize() method.
#             # This method should set up the instance variables it
#             # should use. This is required because the widgets will
#             # come precreated here (think libglade) and we need to
#             # make sure that the variables specific to the subclass
#             # will work.
#             widget._initialize()
#
#     def _sanitize_entry(self, entry):
#         entry.connect("key_press_event", self._entry_key_press_event)
#         entry.connect("focus_in_event", self._entry_focus_in_event)
#         entry.connect("focus_out_event", self._entry_focus_out_event)
#         entry.connect("button_press_event", self._entry_button_press_event)
# 
#     def _sanitize_text(self, text):
#         text.connect("key_press_event", self._check_tab)
# 
#     def _check_tab(self, text, event):
#         if event.keyval == GDK.Tab:
#             text.emit_stop_by_name("key_press_event")
#             return False
#         # If KP_Enter was typed in, produce a newline
#         elif event.keyval == GDK.KP_Enter:
#             text.insert_defaults("\n")
#             text.emit_stop_by_name("key_press_event")
#             return True
#         return False
#     
#     def _entry_key_press_event(self, widget, event, *args):
#         # If escape or ctrl-Z pressed, restore selection
#         if event.keyval in (GDK.Z, GDK.z) and event.state & GDK.CONTROL_MASK:
#             widget.emit_stop_by_name("key_press_event")
#             sel = widget.get_data("_kiwi_selection")
#             if sel:
#                 widget.set_text(sel)
#             return True
#         # If KP_Enter was typed in, skip it
#         elif event.keyval == GDK.KP_Enter:
#             widget.emit_stop_by_name("key_press_event")
#             widget.activate()
#             return True
#         return False
# 
#     def _entry_focus_in_event(self, widget, *args):
#         if not widget.get_data("_kiwi_avoid_select"):
#             widget.select_region(0, -1)
#         widget.set_data("_kiwi_selection", widget.get_text())
#         widget.set_data("_kiwi_avoid_select", 1)
#     
#     def _entry_focus_out_event(self, widget, *args):
#         widget.select_region(0, 0)
#         widget.set_data("_kiwi_avoid_select", 0)
#     
#     def _entry_button_press_event(self, widget, *args):
#         widget.set_data("_kiwi_avoid_select", 1)
#     

class AbstractGladeView:
    """
    Abstract class that does basic Glade file handling. It needs to
    take care of self.widgets as well, since we need to attach the widgets
    specified to the instance. Also offers the _attach_callbacks() hook that
    is important for Controller initialization."""
    gladefile = None
    gladename = None
    tree = None
    def __init__(self, gladefile, widgets):
        """
        Inits the AbstractGladeView. Sets up gladefile, gladename,
        widgets and tree. Attaches named widgets from tree to
        instance."""
        gladefile = gladefile or self.gladefile
        widgets = (widgets or self.widgets or [])[:]

        if not gladefile:
            raise ValueError, "A gladefile wasn't provided."
        elif not isinstance(gladefile, basestring):
            raise TypeError, \
                "gladefile should be a string, found %s" % type(gladefile)

        # get base name of glade file
        if re.match(".+\.glade$", gladefile):
            filename = string.split(gladefile,".glade")[0]
        else:
            filename = gladefile
        
        gladefile = find_in_gladepath(filename + ".glade") 
        # GladeXML accepts a second parameter that allows you to specify
        # a branch of the tree. I initially thought of using
        # toplevel_name, since it would be convenient, but it causes
        # problems for popup menus, since they are top-level items and
        # yet are not commonly wrapped in Views (as Windows or Dialogs
        # would be). This is why we use the simple, one-parameter form.
        self.tree = gtk.glade.XML(gladefile)
        if not self.gladename:
            self.gladename = filename

        # Attachs widgets in the widgetlist to the view specified, so
        # widgets = [ clist1, clist2 ] -> view.clist1, view.clist2
        for w in widgets:
            widget = self.tree.get_widget(w)
            if widget:
                setattr(self, w, widget)
            else:
                _warn("Widget %s was not found in glade widget tree." % w)

        self.widgets = widgets
        self.gladefile = gladefile

    #
    # AbstractView API; this is clobbered in when this class is used as
    # a mixin in Views.py (it's the reason why AbstractGladeView must be
    # the first in the inheritance declaration). 
    #
        
    def get_widget(self, name):
        """Retrieves the named widget from the View (or glade tree)"""
        if not self.tree:
            raise TypeError, \
                "No tree defined for %s, did you call the constructor?" % self
        name = string.replace(name,'.', '_')
        widget = self.tree.get_widget(name)
        if not widget:
            raise AttributeError, \
                "Widget %s not found in view %s" % (name, self)
        return widget

    def _attach_callbacks(self, controller):
        self.__broker = GladeSignalBroker(self, controller)

    #
    # slave handling
    #

    def attach_slave(self, name, slave):
        """
        attaches a slaveview to the current view, substituting the
        widget specified by name.  the widget specified *must* be a
        eventbox; its child widget will be removed and substituted for
        the specified slaveview's toplevel widget::

         .----------------------. the widget that is indicated in the diagram
         |window/view (self)    | as placeholder will be substituted for the 
         |  .----------------.  | slaveview's toplevel.
         |  | eventbox (name)|  |  .-----------------.
         |  |.--------------.|     |slaveview (slave)| 
         |  || placeholder  <---.  |.---------------.|
         |  |'--------------'|   \___ toplevel      ||
         |  '----------------'  |   '---------------'|
         '----------------------'  '-----------------'

        the original way of attachment (naming the *child* widget
        instead of the eventbox) is still supported for compatibility
        reasons but will print a warning."""
        if not isinstance(slave, slaveview) and \
                not isinstance(slave, gladeslaveview):
            _warn("slave specified must be a slaveview "
                  "or gladeslaveview, found %s""" % slave) 

        if not hasattr(slave, "get_toplevel"):
            raise typeerror, "invalid slave"

        shell = slave.get_toplevel()

        if isinstance(shell, gtk.window): # view with toplevel window
            new_widget = shell.get_children()[0]
            shell.remove(new_widget) # remove from window to allow reparent
        else: # slaveview
            new_widget = shell

        placeholder  = self.get_widget(name)
        if not placeholder:
            raise attributeerror, \
                  "slave container widget `%s' not found" % name
        parent = placeholder['parent']           

        if slave._accel_groups:
            # take care of accelerator groups; attach to parent window if we
            # have one; if embedding a slave into another slave, store its
            # accel groups; otherwise complain if we're dropping the accelerators
            win = parent.get_toplevel()
            if isinstance(win, gtk.window):
                # use idle_add to be sure we attach the groups as late
                # as possible and avoid reattaching groups -- see
                # comment in _attach_groups.
                gtk.idle_add(self._attach_groups, win, slave._accel_groups)
            elif isinstance(self, slaveview) or isinstance(self, gladeslaveview):
                self._accel_groups.extend(slave._accel_groups)
            else:
                _warn("attached slave %s to parent %s, but parent lacked "
                      "a window and was not a slave view" % (slave, self))
            slave._accel_groups = []

        if isinstance(placeholder, gtk.eventbox):
            # standard mechanism
            children = placeholder.get_children()
            if len(children): 
                placeholder.remove(children[0])
            placeholder.add(new_widget)
        elif isinstance(parent, gtk.eventbox):
            # backwards compatibility
            _warn("attach_slave's api has changed: read docs, update code!")
            parent.remove(placeholder)
            parent.add(new_widget)
        else:
            raise typeerror, \
                "widget to be replaced must be wrapped in eventbox"
     
        # call slave's callback
        slave.on_attach(self)

        # return placeholder we just removed
        return placeholder

    def _attach_groups(self, win, accel_groups):
        # get groups currently attached to the window; we use them
        # to avoid reattaching an accelerator to the same window, which
        # generates messages like:
        #
        # gtk-critical **: file gtkaccelgroup.c: line 188
        # (gtk_accel_group_attach): assertion `g_slist_find
        # (accel_group->attach_objects, object) == null' failed.
        #
        # interestingly, this happens many times with notebook,
        # because libglade creates and attaches groups in runtime to
        # its toplevel window.
        current_groups = gtk_accel_groups_from_object(win._o)
        for group in accel_groups:
            if group in current_groups:
                # skip group already attached
                continue
            real_group = gtk.accelgroup(group)
            win.add_accel_group(real_group)
