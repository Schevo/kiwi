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
#            Jon Nelson <jnelson@securepipe.com>
#            Lorenzo Gil Sanchez <lgs@sicem.biz>
#            Johan Dahlin <jdahlin@async.com.br>
#            Henrique Romano <henrique@async.com.br>
#

"""
Defines the View classes that are included in the Kiwi Framework, which
are the base of Delegates and Proxies.
"""
import os, string, sys

from Kiwi2 import _warn, get_gladepath, get_imagepath
from Kiwi2.utils import gsignal
from Kiwi2.initgtk import _non_interactive, gtk, gobject, quit_if_last
from Kiwi2.Proxies import Proxy
from Kiwi2.Widgets import WidgetProxy

#
# Gladepath handling
#

def find_in_gladepath(filename):
    """Looks in gladepath for the file specified"""

    gladepath = get_gladepath()
    
    # check to see if gladepath is a list or tuple
    if not isinstance(gladepath, (tuple, list)):
        msg ="gladepath should be a list or tuple, found %s"
        raise ValueError(msg % type(gladepath))
    if os.sep in filename or not gladepath:
        if os.path.isfile(filename):
            return filename
        else:
            raise IOError("%s not found" % filename)

    for path in gladepath:
        # append slash to dirname
        if not path:
            continue
        # if absolute path
        fname = os.path.join(path, filename)
        if os.path.isfile(fname):
            return fname

    raise IOError("%s not found in path %s.  You probably need to "
                  "Kiwi.set_gladepath() correctly" % (filename, gladepath))

#
# Image path resolver
#

def image_path_resolver(filename):
    imagepath = get_imagepath()

    # check to see if imagepath is a list or tuple
    if not isinstance(imagepath, (list, tuple)):
        msg ="imagepath should be a list or tuple, found %s"
        raise ValueError(msg % type(imagepath))

    if not imagepath:
        if os.path.isfile(filename):
            return filename
        else:
            raise IOError("%s not found" % filename)

    basefilename = os.path.basename(filename)
    
    for path in imagepath:
        if not path:
            continue
        fname = os.path.join(path, basefilename)
        if os.path.isfile(fname):
            return fname

    raise IOError("%s not found in path %s. You probably need to "
                  "Kiwi.set_imagepath() correctly" % (filename, imagepath))

#
# Signal brokers
#

class SignalBroker(object):
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
            if widget is None:
                raise AttributeError("couldn't find widget %s in %s"
                                     % (w_name, view))
            if not isinstance(widget, (gtk.Widget, gtk.Action)):
                raise AttributeError("%s (%s) is not a widget or an action "
                                     "and can't be connected to"
                                     % (w_name, widget))
            # Must use getattr; using the class method ends up with it
            # being called unbound and lacking, thus, "self".
            try:
                if after:
                   signal_id = widget.connect_after(signal, methods[fname])
                else:
                   signal_id = widget.connect(signal, methods[fname])
            except TypeError:
                raise AttributeError("Widget %s doesn't provide a signal %s"
                                     % (widget.__class__, signal))
            if not self._autoconnected.has_key(widget):
                self._autoconnected[widget] = []
            self._autoconnected[widget].append((signal, signal_id))

    def handler_block(self, widget, signal_name):
        signals = self._autoconnected
        if not widget in signals:
            return
            
        for signal, signal_id in signals[widget]:
            if signal_name is None or signal == signal_name:
                widget.handler_block(signal_id)

    def handler_unblock(self, widget, signal_name):
        signals = self._autoconnected
        if not widget in signals:
            return
        
        for signal, signal_id in signals[widget]:
            if signal_name is None or signal == signal_name:
                widget.handler_unblock(signal_id)

    def disconnect_autoconnected(self):
        for widget, signals in self._autoconnected.items():
            for unused, signal_id in signals:
                widget.disconnect(signal_id)
        
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
            raise AssertionError("controller must be provided")

        dict = {}
        for name, method in methods.items():
            if callable(method):
                dict[name] = method
        view.glade_adaptor.signal_autoconnect(dict)
        

class SlaveView(gobject.GObject):
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
    toplevel_name = None
    gladefile = None
    gladename = None

    # This signal is emited when the view wants to return a result value
    gsignal("result", object)
    
    def __init__(self, toplevel=None, widgets=None, gladefile=None,
                 gladename=None, toplevel_name=None):
        """ Creates a new SlaveView. Sets up self.toplevel and self.widgets
        and checks for reserved names.
        """
        gobject.GObject.__init__(self)

        # setup the initial state with the value of the arguments or the
        # class variables

        if not gladefile:
            gladefile = self.gladefile
        if not gladename:
            gladename = self.gladename
        if not toplevel_name:
            toplevel_name = self.toplevel_name
        if not toplevel:
            toplevel = self.toplevel
        self.gladefile = gladefile
        self.gladename = gladename
        self.toplevel_name = toplevel_name
        self.toplevel = toplevel
        self.widgets = widgets or self.widgets or []
        
        # stores the function that will be called when widgets 
        # validity is checked
        self._validate_function = None
        
        for reserved in ["widgets", "toplevel", "gladefile",
                         "gladename", "tree", "model", "controller"]:
            # XXX: take into account widget constructor?
            if reserved in self.widgets:
                raise AttributeError("The widgets list for %s contains "
                                     "a widget named `%s', which is "
                                     "a reserved. name""" % (self, reserved))


        self.glade_adaptor = None
        if self.gladefile is not None:
            self._init_glade_adaptor()

        if self.toplevel_name is not None and self.toplevel is None:
            self.toplevel = getattr(self, self.toplevel_name, None)
        
        if not self.toplevel:
            raise TypeError("A View requires an instance variable "
                            "called toplevel that specifies the "
                            "toplevel widget in it")


        self.proxies = []
        
        # grab the accel groups
        self._accel_groups = gtk.accel_groups_from_object(self.toplevel)

        self.slaves = {}

    # Global validations
    def check_widgets_validity(self):
        """Checks if there are widgets with invalid data.
        Calls the registered validate function
        """
        if self._validate_function is None:
            return
        valid = True
        for widget_name in self.widgets:
            widget = self.get_widget(widget_name)
            if isinstance(widget, WidgetProxy.MixinSupportValidation):
                if not widget.is_correct():
                    valid = False
                    break

        self._validate_function(valid)

    def register_validate_function(self, function):
        """The signature of the validate function is:

        def function(is_valid):

        or, if it is a method:

        def function(self, is_valid):

        where the 'is_valid' parameter is True if all the widgets have
        valid data or False otherwise.
        """
        self._validate_function = function

    def _init_glade_adaptor(self):
        """Special init code that subclasses may want to override."""
        self.glade_adaptor = GazpachoWidgetTree(self, self.gladefile,
                                                self.widgets, self.gladename)

        container_name = self.toplevel_name or self.gladename or self.gladefile
            
        if container_name is None:
            msg = ("You provided a gladefile %s to grab the widgets from "
                   "but you didn't give me a toplevel/container name!")
            raise ValueError(msg % self.gladefile)

        # a SlaveView inside a glade file needs to come inside a toplevel
        # window, so we pull our slave out from it, grab its groups and
        # muerder it later
        shell = self.glade_adaptor.get_widget(container_name)
        if not isinstance(shell, gtk.Window):
            msg = "Container %s should be a Window, found %s"
            raise TypeError(msg % (container_name, type(shell)))

        # XXX grab the accel groups

        self.toplevel = shell.get_child()
        shell.remove(self.toplevel)
        shell.destroy()

    #
    # Hooks
    #

    def on_attach(self, parent):
        """ Hook function called when attach_slave is performed on slave views.
        """
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
            raise AttributeError("Widget %s not found in view %s"
                                 % (name, self))
        if not isinstance(widget, gtk.Widget):
            raise TypeError("%s in view %s is not a Widget"
                            % (name, self))
        return widget

    def set_controller(self, controller):
        """
        Sets the view's controller, checking to see if one has already
        been set before."""
        # Only one controller per view, please
        if self.controller:
            raise AssertionError("This view already has a controller: %s"
                                 % self.controller)
        self.controller = controller

    #
    # GTK+ proxies and convenience functions
    #

    def show(self, *args):
        """Shows the toplevel widget"""
        self.toplevel.show()

    def show_all(self, *args):
        """Shows all widgets attached to the toplevel widget"""
        if self.glade_adaptor is not None:
            raise AssertionError("You don't want to call show_all on a "
                                 "GazpachoView. Use show() instead.")
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
                
            if top_widget:
                allocation = widget.allocation
                top_allocation = getattr(top_widget, 'allocation',  None)
                assert top_allocation != None
                if (top_allocation[0] + top_allocation[1] >
                    allocation[0] + allocation[1]):
                    top_widget = widget
            else:
                top_widget = widget
        return top_widget

    #
    # Callback handling
    #

    def _attach_callbacks(self, controller):
        if self.glade_adaptor is None:
            brokerclass = SignalBroker
        else:
            brokerclass = GladeSignalBroker
            
        self.__broker = brokerclass(self, controller)

#    def _setup_keypress_handler(self, keypress_handler):
#        # Only useful in BaseView and derived classes
#        # XXX: support slaveview correctly
#        _warn("Tried to setup a keypress handler for %s "
#              "but no toplevel window exists to attach to" % self)

    #
    # Slave handling
    #
    def attach_slave(self, name, slave):
        """Attaches a slaveview to the current view, substituting the
        widget specified by name.  the widget specified *must* be a
        eventbox; its child widget will be removed and substituted for
        the specified slaveview's toplevel widget::

         .-----------------------. the widget that is indicated in the diagram
         |window/view (self.view)| as placeholder will be substituted for the 
         |  .----------------.   | slaveview's toplevel.
         |  | eventbox (name)|   |  .-----------------.
         |  |.--------------.|      |slaveview (slave)| 
         |  || placeholder  <----.  |.---------------.|
         |  |'--------------'|    \___ toplevel      ||
         |  '----------------'   |  ''---------------'|
         '-----------------------'  '-----------------'

        the original way of attachment (naming the *child* widget
        instead of the eventbox) is still supported for compatibility
        reasons but will print a warning.
        """
        if not isinstance(slave, SlaveView):
            _warn("slave specified must be a SlaveView, found %s" % slave)

        if not hasattr(slave, "get_toplevel"):
            raise TypeError("Slave does not have a get_toplevel method")

        shell = slave.get_toplevel()

        if isinstance(shell, gtk.Window): # view with toplevel window
            new_widget = shell.get_child()
            shell.remove(new_widget) # remove from window to allow reparent
        else: # slaveview
            new_widget = shell

        # if our widgets are in a glade file get the placeholder from them
        # or take it from the view itself otherwise
        if self.glade_adaptor:
            placeholder = self.glade_adaptor.get_widget(name)
        else:
            placeholder = getattr(self, name, None)
            
        if not placeholder:
            raise AttributeError(
                  "slave container widget `%s' not found" % name)
        parent = placeholder.get_parent()

        if slave._accel_groups:
            # take care of accelerator groups; attach to parent window if we
            # have one; if embedding a slave into another slave, store its
            # accel groups; otherwise complain if we're dropping the accelerators
            win = parent.get_toplevel()
            if isinstance(win, gtk.Window):
                # use idle_add to be sure we attach the groups as late
                # as possible and avoid reattaching groups -- see
                # comment in _attach_groups.
                gtk.idle_add(self._attach_groups, win, slave._accel_groups)
            elif isinstance(self, SlaveView):
                self._accel_groups.extend(slave._accel_groups)
            else:
                _warn("attached slave %s to parent %s, but parent lacked "
                      "a window and was not a slave view" % (slave, self))
            slave._accel_groups = []

        if isinstance(placeholder, gtk.EventBox):
            # standard mechanism
            child = placeholder.get_child()
            if child is not None:
                placeholder.remove(child)
            placeholder.add(new_widget)
        elif isinstance(parent, gtk.EventBox):
            # backwards compatibility
            _warn("attach_slave's api has changed: read docs, update code!")
            parent.remove(placeholder)
            parent.add(new_widget)
        else:
            raise TypeError(
                "widget to be replaced must be wrapped in eventbox")

        # when attaching a slave we usually want it visible
        parent.show()
        
        # call slave's callback
        slave.on_attach(self)

        if self.slaves.has_key(name):
            # I prefer to don't emit a raise here because it's really
            # possible to change a certain slave in runtime.
            _warn("You already have a slave %s attached" % name)
        self.slaves[name] = slave

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
        current_groups = gtk.accel_groups_from_object(win)
        for group in accel_groups:
            if group in current_groups:
                # skip group already attached
                continue
            win.add_accel_group(group)

    def get_slave(self, holder):
        if self.slaves.has_key(holder):
            return self.slaves[holder]
        raise AttributeError, "Unknown slave for holder: %s" % holder


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
            raise TypeError("widgets must be a list, found %s" % widgets)
        for widget in widgets:
            if not isinstance(widget, gtk.Widget):
                raise TypeError(
                "Only Gtk widgets may be passed in list, found\n%s" % widget)
            if after:
                widget.connect_after(signal, handler)
            else:
                widget.connect(signal, handler)

    def disconnect_autoconnected(self):
        """
        Disconnect handlers previously connected with 
        autoconnect_signals()"""
        self.__broker.disconnect_autoconnected()
        
    def handler_block(self, widget, signal_name=None):
        self.__broker.handler_block(widget, signal_name)

    def handler_unblock(self, widget, signal_name=None):
        self.__broker.handler_unblock(widget, signal_name)
        
    #
    # Proxies
    #

    def add_proxy(self, model=None, widgets=None):
        """
        Add a proxy to this view that automatically update a model when
        the view changes. Arguments:
          
          - model. the object we are proxing. It can be None if we don't have
          a model yet and we want to display the interface and set it up with
          future models.
          - widgets. the list of widgets that contains model attributes to be
          proxied. If it is None (or not specified) it will be the whole list
          of widgets this View has.

        This method return a Proxy object that you may want to use to force
        updates or setting new models. Keep a reference to it since there is
        no way to get that proxy later on. You have been warned (tm)
        """
        widgets = widgets or self.widgets
        proxy = Proxy(self, model, widgets)
        self.proxies.append(proxy)
        return proxy
    
gobject.type_register(SlaveView)

class BaseView(SlaveView):
    """A view with a toplevel window."""
    
    def __init__(self, toplevel=None, delete_handler=None, widgets=None,
                 gladefile=None, gladename=None, toplevel_name=None):
        """ toplevel is the widget to be set as `toplevel' (and which will
        be aliased as `win'); delete_handler allows setting a function
        to be called when this view's window is deleted."""
        try:
            SlaveView.__init__(self, toplevel, widgets, gladefile, gladename,
                               toplevel_name)
        except KeyError:
            raise KeyError("Some widgets were defined in self.widgets "
                           "but not found in the glade tree (see previous "
                           "messages to see which ones).")
            

        if not isinstance(self.toplevel, gtk.Window):
            raise TypeError("toplevel widget must be a Window "
                            "(or inherit from it),\nfound `%s' %s" 
                            % (toplevel, self.toplevel))

        if delete_handler:
            id = self.toplevel.connect("delete_event", delete_handler)
            if not id:
                raise ValueError(
                    "Invalid delete handler provided: %s" % delete_handler)

    def _init_glade_adaptor(self):
        self.glade_adaptor = GazpachoWidgetTree(self, self.gladefile,
                                                self.widgets, self.gladename)
        name = self.toplevel_name or self.glade_adaptor.gladename
        self.toplevel = self.glade_adaptor.get_widget(name)

        if self.toplevel.flags() & gtk.VISIBLE:
            _warn("Toplevel widget %s (%s) is visible; that's probably "
                  "wrong" % (self.toplevel, name))
            
    
    #
    # Hook for keypress handling
    #

    def _attach_callbacks(self, controller):
        super(BaseView, self)._attach_callbacks(controller)
        self._setup_keypress_handler(controller.on_key_press)
        
    def _setup_keypress_handler(self, keypress_handler):
        self.toplevel.connect_after("key_press_event", keypress_handler)

    #
    # Proxying for self.toplevel
    #
    def set_transient_for(self, view):
        """Makes the view a transient for another view; this is commonly done
        for dialogs, so the dialog window is managed differently than a
        top-level one.
        """
        if hasattr(view, 'toplevel') and isinstance(view.toplevel, gtk.Window):
            self.toplevel.set_transient_for(view.toplevel)
        # In certain cases, it is more convenient to send in a window;
        # for instance, in a deep slaveview hierarchy, getting the
        # top view is difficult. We used to print a warning here, I
        # removed it for convenience; we might want to put it back when
        # http://bugs.async.com.br/show_bug.cgi?id=682 is fixed
        elif isinstance(view, gtk.Window):
            self.toplevel.set_transient_for(view)
        else:
            raise TypeError("Parameter to set_transient_for should "
                            "be View (found %s)" % view)

    def set_title(self, title):
        """Sets the view's window title"""
        self.toplevel.set_title(title)

    #
    # Focus handling
    #

    def get_focus_widget(self):
        """Returns the currently focused widget in the window"""
        return self.toplevel.focus_widget

    def check_focus(self):
        """ Tests the focus in the window and prints a warning if no
        widget is focused.
        """
        focus = self.toplevel.focus_widget
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
            _warn("No widget is focused in view %s but you have an "
                  "interactive widget in it: %s""" % (self, interactive))

    #
    # Window show/hide and mainloop manipulation
    #

    def hide(self, *args):
        """Hide the view's window"""
        self.toplevel.hide()

    def show_all(self, parent=None, *args):
        self.toplevel.show_all()
        self.show(parent, *args)

    def show(self, parent=None, *args):
        """Show the view's window.
        If the parent argument is supplied and is a valid view, this view
        is set as a transient for the parent view.
        """
        # Uniconize window if minimized
        self.toplevel.present() # this call win.show() for us
        self.check_focus()
        if parent is not None:
            self.set_transient_for(parent)

    def hide_and_quit(self, *args):
        """Hides the current window and breaks the GTK+ event loop if this
        is the last window.
        Its method signature allows it to be used as a signal handler.
        """
        self.toplevel.hide()
        quit_if_last(*args)

#
#
#


class GladeAdaptor(object):
    """Abstract class that define the functionality an class that handle
    glade files should provide."""

    def get_widget(self, widget_name):
        """Return the widget in the glade file that has that name"""

    def get_widgets(self):
        """Return a tuple with all the widgets in the glade file"""

    def attach_slave(self, name, slave):
        """Attaches a slaveview to the view this adaptor belongs to,
        substituting the widget specified by name.
        The widget specified *must* be a eventbox; its child widget will be
        removed and substituted for the specified slaveview's toplevel widget
        """

    def signal_autoconnect(self, dic):
        """Connect the signals in the keys of dict with the objects in the
        values of dic
        """
    
from gazpacho.loader import widgettree

class GazpachoWidgetTree(GladeAdaptor):
    """Example class of GladeAdaptor that uses Gazpacho loader to load the
    glade files
    """
    tree = None
    def __init__(self, view, gladefile, widgets, gladename=None):
        self.view = view
        
        widgets = (widgets or self.view.widgets or [])[:]
        
        if not gladefile:
            raise ValueError("A gladefile wasn't provided.")
        elif not isinstance(gladefile, basestring):
            raise TypeError(
                  "gladefile should be a string, found %s" % type(gladefile))
        
        # get base name of glade file
        basename = os.path.basename(gladefile)
        filename = os.path.splitext(basename)[0]
        
        gladefile = find_in_gladepath(filename + ".glade")
        self.tree = widgettree.WidgetTree(gladefile,
                                          path_resolver=image_path_resolver)
        self.gladename = gladename or filename
            
        
        # Attach widgets in the widgetlist to the view specified, so
        # widgets = [label1, button1] -> view.label1, view.button1
        for w in widgets:
            widget = self.tree.get_widget(w)
            if widget is not None:
                setattr(self.view, w, widget)
            else:
                _warn("Widget %s was not found in glade widget tree." % w)
        
        self.widgets = widgets
        self.gladefile = gladefile
        
    def get_widget(self, name):
        """Retrieves the named widget from the View (or glade tree)"""
        if self.tree is None:
            raise TypeError(
                  "No tree defined for %s, did you call the constructor?" % self.view)
        name = name.replace('.', '_')
        widget = self.tree.get_widget(name)
        if widget is None:
            raise AttributeError(
                  "Widget %s not found in view %s" % (name, self.view))
        return widget

    def get_widgets(self):
        return self.tree.get_widgets()

    def signal_autoconnect(self, dic):
        self.tree.signal_autoconnect(dic)        
