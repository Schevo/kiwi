#!/usr/bin/env python
#
# Kiwi: a Framework and Enhanced Widgets for Python
#
# Copyright (C) 2002-2004 Async Open Source
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

"""
This module defines the Proxy classes, which are a special type of
Delegate that connect the interface widgets to a Model instance. Proxies
allow changes in the widgets to map transparently to changes in the
model.
"""

import string, sys
from types import StringType, ListType, TupleType, DictType

from Kiwi import _warn, USE_MX, get_decimal_separator, ValueUnset
from Kiwi.initgtk import gtk

from Kiwi.Controllers import BaseController
from Kiwi.Views import SlaveView, GladeView, GladeSlaveView, BaseView
from Kiwi.Delegates import SlaveDelegate, GladeSlaveDelegate, GladeDelegate, \
                      Delegate

from Kiwi.accessors import kgetattr, ksetattr, clear_attr_cache
from Kiwi.WidgetProxies import standard_widgets, RadioGroup #, Entry
#from Kiwi.Basic import Combo, AutoCombo

#
# Warning system
#

PROXY_WARNINGS = 1
ATTR_WARNINGS = 0

def set_proxy_warnings(state=True):
    """
    Enable warnings to be emitted from Proxies when incorrect (or very
    unusual) use is detected. This should always be enabled, as it is a
    good way of detecting programming errors."""
    global PROXY_WARNINGS
    PROXY_WARNINGS = state

def set_attr_warnings(state=True):
    """
    Enables warnings for direct attribute access. If called, all direct
    accesses done to the model instance will be warned. Use this to
    check for the completeness of your model accessor API, if you have
    decided to define one."""
    global ATTR_WARNINGS
    ATTR_WARNINGS = state

def _attrwarn(msg):
    if ATTR_WARNINGS:
        _warn(msg)

#
# Abstract Class
#

class VirtualProxy:
    """
    A Proxy is a class that `attaches' an instance to an interface's
    widgets, and transparently manipulates that instance's attributes as
    the user alters the content of the widgets. The widgets in the
    interface are associated to instance attributes by specifying names
    prefixed with `:' in the widgets list that is used normally in
    Views. The names (stripped of the leading colon) specify both the
    widget name in the View as the instance attribute (though accessors
    like get_name() and set_name(value) will be used if they exist).

    In other words, use widgets as you normally would for Views, but
    prefix the ones that correspond to Model attributes with `:'. You
    might end up with something like::

        self.widgets = [
            ":name",      
            ":phone",
            ":address",
            "okbutton",
            "cancel"
        ]

    Where your instance holds variables named `name', `phone' and `address'
    (or get_name()/set_name() etc), and there are widgets with the same name
    defined in your View or glade file.
    """

    model = None
    _conversion_errors = None
    _setter_error_handler = None
    def __init__(self, model=None):
        """
        The VirtualProxy constructor should be called *before*
        FrameWork.BaseController.__init__ or bad things happen. Keep
        this in mind.

            - model: the model instance to be attached to the proxy. 
    
        If model is None, the interface will be displayed as-is and no
        changes to it will be caught. *Danger*: any data entered in the
        widgets will be used as a *default* for the next model, so be
        sure to make the parts that contain the widgets read-only and/or
        insensitive.
        """
        self._attr_map = {}
        self._proxy_map ={}
     
        if not hasattr(self, "_decimal_separator"):
            self._decimal_separator = None
            self._decimal_translator = None
            # get this as late as we can to make sure we get it updated
            sep = get_decimal_separator()
            if sep:
                self.set_decimal_separator(sep)

        self._setup_state()
        self._setup_widgets()
        self.model = model

    # Called externally from special subclasses. Double-underscore
    # protects "normal" subclasses.
    def __initialize(self):
        # Now that the widgets have been set up, update their contents
        for name, proxy in self._attr_map.items():

            if self.model is None:
                # if we have no model, leave value unset so we pick up
                # the widget default below.
                value = ValueUnset
            else:
                # if we have a model, grab its value to update the widgets
                self._register_proxy_in_model(name)
                value = kgetattr(self.model, name, ValueUnset)

            if value is ValueUnset:
                # grab default in widget, converting it as necessary
                if proxy.converted:
                    value = proxy.read_converted(proxy.default)
                else:
                    value = proxy.default

            update = getattr(self, "tweak_%s" % name, None) or \
                     self.update
            update(name, value)

    def set_setter_error_handler(self, handler):
        """
        Sets a method that will be called if an update to a model
        attribute raises an exception. The handler will receive the
        following arguments, in order:

            - Exception object
            - model
            - attribute name
            - value attempted
        """
        self._setter_error_handler = handler

    def enable_conversion_errors(self):
        """XXX"""
        self._conversion_errors = True

    def notify(self, name, value=ValueUnset):
        """
        Notifies the proxy that the named attribute has changed. Calls by
        default tweak_foo if the name provided is "foo" and update_foo
        exists. This should *only* be called by the FrameWork Model, not by an
        end-user callback.

            - name: the name of the attribute being changed
            - value: what it was set to
        """
        func = getattr(self, "tweak_%s" % name, None)
        if func:
            # If value is unset, send in model value to tweak_%s
            if value is ValueUnset:
                value = kgetattr(self.model, name, ValueUnset)
                if value is ValueUnset:
                    raise ValueError, "model value for %s was unset" % name
            func(name, value)
        else:
            self.update(name, value, block=True)

    def proxy_updated(self, widgetproxy, value):
        """
        This is a hook that is called whenever the proxy updates the
        model. Implement it in the inherited class to perform actions that
        should be done each time the user changes something in the interface.
        This hook by default does nothing.
        """
        pass

    def update(self, name, value=ValueUnset, block=False):
        """
        Generic frontend function to update the contents of a widget based on
        its name using the internal update functions. 

            - name: the name of the attribute whose widget we wish to
              updated.  If accessing a radiobutton, specify its group
              name. 
            - value specifies the value to set in the widget. If
              unspecified, it defaults to the current model's value
              (through an accessor, if it exists, or getattr). 
            - block defines if we are to block cascading proxy updates
              triggered by this update. You should use block if you are
              calling update on *the same attribute that is currently
              being updated*.

              This means if you have hooked to a signal of the widget
              associated to that attribute, and you call update() for
              the *same attribute*, use block=True. And pray. 8). If
              block is set to False, the normal update mechanism will
              occur (the model being updated in the end, hopefully).
        """

        if value is ValueUnset:
        # We want to obtain a value from our model
            if self.model is None:
                # We really want to avoid trying to update our UI if our
                # model doesn't exist yet and no value was provided.
                # update() is also called by user code, but it should be
                # safe to return here since you shouldn't need to code
                # around the lack of a model in your callbacks if you
                # can help it.
                return
            value = kgetattr(self.model, name, ValueUnset)
            if value is ValueUnset:
                raise ValueError, "Tried to update %s to unset value" % name

        widgetproxy = self._attr_map.get(name, None)

        if not widgetproxy:
            raise AttributeError, ("Called update for `%s', which isn't "
                                   "attached to the proxy %s. Valid "
                                   "attributes are: %s (you may have "
                                   "forgetten to add `:' to the name in "
                                   "the widgets list)" 
                                   % (name, self, self._attr_map.keys()))

        if block:
            widgetproxy.block = True
            widgetproxy.update(value)
            widgetproxy.block = False
        else:
            widgetproxy.update(value)
        return True

    def new_model(self, new_model, relax_type=False):
        """
        Reuses the same proxy with another instance as model. Allows a
        proxy interface to change model without the need to destroy and
        recreate the UI (which would cause flashing, at least)
        """
        # unregister previous proxy
        if self.model and hasattr(self.model, "unregister_proxy"):
            self.model.unregister_proxy(self)

        # the following isn't strictly necessary, but it currently works
        # around a bug with reused ids in the attribute cache and also
        # makes a lot of sense for most applications (don't want a huge
        # eternal cache pointing to models that you're not using anyway)
        clear_attr_cache()

        if self.model is not None:
            assert self.model.__class__
            if not relax_type and type(new_model) != type(self.model) and \
                not isinstance(new_model, self.model.__class__):
                raise TypeError, "New model has wrong type %s, expected %s" \
                                 % (type(new_model), type(self.model))

        self.model = new_model

        # During the initialization, the OptionMenu needs to preserve
        # the original model value, which is why we use this ha^Wlock.
        self._avoid_clobber = True
        self.__initialize()
        self._avoid_clobber = False
    
    def refresh_optionmenu(self, attr_name, preserve_model_value=0):
        """
        Notifies the proxy that one or more menuitems of an optionmenu
        have been changed. attr_name is the name of the attribute; use
        the dotted form ("foo.bar") for sub-attributes.

            - attr_name: The name of the attribute to which the
              optionmenu is associated
            - preserve_model_value: A boolean specifying if we should
              try to preserve the previous model value or just set it to
              the default in the new optionmenu list.
        """
        if type(attr_name) is not StringType:
            msg = "Expected the attribute name (a string), got %s instead"
            raise TypeError, msg % attr_name
        if not hasattr(self, "_attr_map"):
            raise ValueError, "Don't call this before Proxy.__init__()"
        optionmenu = self._attr_map[attr_name]
        optionmenu.setup()
        data = optionmenu.read()
        optionmenu.default = data

        if preserve_model_value:
            value = kgetattr(self.model, attr_name, ValueUnset)
            # if model specified a value, use it
            if value is not ValueUnset and value is not None:
                data = value

        optionmenu.update(data)

    def group_radiobuttons(self, name, group):
        """
        Groups a set of radiobuttons to a single model attribute. 

            - name: the name of the model attribute the group will be
              associated with. Use the dotted form ("foo.bar") for
              sub-attributes.
            - group: the group parameter is either a list of widget
              names or a mapping from widget name to widget data. If a
              mapping is provided, the model attribute will be set to
              the value specified in data; if not, it will be set to the
              button label.
        """
        grouptype = type(group)
        if hasattr(self, "_attr_map"):
            raise AssertionError, ("group_radiobuttons() must be called "
                                   "before the constructor for *Proxy")
        if grouptype in (ListType, TupleType):
            tmp = {}
            for widget_name in group:
                # ValueUnset is fixed in RadioGroup.__init__
                tmp[widget_name] = ValueUnset
            group = tmp
        elif grouptype != DictType:
            msg = "group must be DictType or Sequence, found %s"
            raise TypeError, msg % grouptype
        # Finally initialize radiogroups. This is done here because it
        # has to be done before __init__(), and I'm not sure if doing it
        # in the class declaration is without its risks
        self._radiogroups = getattr(self, "_radiogroups", {})
        self._radiogroups[name] = group

    def set_datetime(self, widget_names):
        if not USE_MX:
            raise TypeError, \
                "DateTime support is not available. Please install mxDateTime"
        if hasattr(self, "_attr_map"):
            raise AssertionError, ("set_datetime() must be called before "
                                   "the constructor for the base Proxy class")
        if type(widget_names) == StringType:
            widget_names = [widget_names]
        elif type(widget_names) not in (TupleType, ListType):
           raise TypeError, ("widget_names parameter to set_datetime "
                             "should be a string or a list of strings, "
                             "found '%s'" % (widget_names))
        self._pre_datetime = getattr(self, "_pre_datetime", [])
        self._pre_datetime.extend(widget_names)

    def set_format(self, widget_names, format):
        """
        Sets a format for the data displayed and held in a widget. Format
        applies to any value that is set in the model, ** excluding the empty
        string ("") and None ** (these will be displayed as empty strings).

        When using attributes that have been set_datetime() the format string
        should be a string suitable for strftime().

            - widget_names: a single widget name, or a list of widget *names*.
              Each widget must be a "text" widget like GtkText, GtkEntry,
              GtkLabel, GtkSpinButton or GtkCombo. Passing in invalid widgets
              will *fail silently* so be careful. You have been warned!
            - format: a Python format string in the standard "%x.yt" form, or,
              in the case of datetime attributes, in the strftime() format.
        """
        # XXX: this function only really makes sense for Editables
        if type(widget_names) == StringType:
            widget_names = [widget_names]
        elif type(widget_names) not in (TupleType, ListType):
           raise TypeError, ("widget_names parameter to set_format should "
                             "be a string or a list of strings, found %r" 
                             % (widget_names))
        if type(format) != StringType:
           raise TypeError, ("format parameter to set_format should "
                             "be a string, found %r" % (format))
        # Check if setup_widgets has run
        if hasattr(self, "_attr_map"):
            raise AssertionError, ("set_format() must be called before "
                                   "the constructor for *Proxy")
        self._pre_formats = getattr(self, "_pre_formats", {})
        # process list of names
        # XXX: we could be smarter about format strings and their
        # relation with numeric.
        for widget_name in widget_names:
            self._pre_formats[widget_name] = format

    def set_decimal_separator(self, char):
        """
        Changes the decimal separator for numeric types from the default dot
        (.) to another character.
        """
        if type(char) != StringType or len(char) != 1:
            raise ValueError, "Must be a single char, got %s" % char
        self._decimal_separator = char
        self._decimal_translator = string.maketrans(".%s" % char, 
                                                    "%s." % char)

    def set_numeric(self, widget_names):
        """
        Informs the Proxy that the field(s) specified are to be
        handled as numeric (making sure that appropriate conversion is done
        to/from the model value)

            - widget_names: list of widget names (strings). A single string can
              also be provided, like in set_format().
        """
        # XXX: only realy makes sense for Editables
        if hasattr(self, "_attr_map"):
            raise AssertionError, ("set_format() must be called before "
                                   "the constructor for the base Proxy class")
        if type(widget_names) == StringType:
            widget_names = [widget_names]
        elif type(widget_names) not in (TupleType, ListType):
           raise TypeError, ("widget_names parameter to set_format "
                             "should be a string or a list of strings, "
                             "found '%s'""" % (widget_names))
        self._pre_numeric = getattr(self, "_pre_numeric", [])
        # process list of names
        self._pre_numeric.extend(widget_names)

    #    
    # "below are the guts<tm>"
    #

    def _parse_widgets(self, widgets=None):
        # This should be called before initialization of the Proxy
        # Basically exists to parse the widgets list and create a list
        # of proxy attributes (which are prefixed with : in the widgets
        # list)
        #
        # XXX: this will need to be changed for composition

        attrs = []
        widgets = (widgets or self.widgets or [])[:]
        
        for i in range(0, len(widgets)):
            name = widgets[i]
            if name[0] == ":":
                if name[0:2] == "::":
                    raise SyntaxError, ("Specify attributes with a single "
                                        "colon before the name; multiple "
                                        "colons are not allowed.")
                name = name[1:]
                widget_name = name
                if string.find(widget_name, '.') != -1:
                    widget_name = string.replace(name, ".","_")
                if widget_name in widgets:
                    raise ValueError, ("widgets list for %s already contains "
                                       "a %r widget" % (self, widget_name))
                attrs.append(name)   
                widgets[i] = widget_name

        self._attrs = attrs
        return widgets
    
    def _setup_state(self): 
        # see _parse_widgets
        self._attrs = getattr(self, "_attrs", [])

        # see group_radiobuttons and set_*
        self._radiogroups = getattr(self, "_radiogroups", {})
        self._pre_formats = getattr(self, "_pre_formats", {})
        self._pre_numeric = getattr(self, "_pre_numeric", [])
        self._pre_datetime = getattr(self, "_pre_datetime", [])
        
        self._avoid_clobber = False

    def _setup_widgets(self):
        # Instantiates WidgetProxies, sets the relevant parameters,
        # and saves the default.
        pre_formats = self._pre_formats
        pre_datetime = self._pre_datetime
        pre_numeric = self._pre_numeric

        for attr_name in self._attrs:
            widget = self._get_widget_by_name(attr_name)

            # radiobuttons are special-cased because of groups; just
            # check if they exist and set them up at the end
            if isinstance(widget, gtk.RadioButton):
                self._check_radiobutton(attr_name)
                continue

#             if isinstance(widget, AutoCombo):
#                 widgetproxy = Entry.AutoComboProxy(self, widget, attr_name)
#             elif isinstance(widget, Combo):
#                 widgetproxy = Entry.KiwiComboProxy(self, widget, attr_name)
#            else:
            if 1:
                try:
                    wpklass = standard_widgets[widget.__class__]
                except KeyError:
                    raise TypeError, "No proxy widget defined for %r %s\n" \
                        % (attr_name, widget)
                widgetproxy = wpklass(self, widget, attr_name)

            # XXX: move these out when Widget() is implemented
            if pre_formats.has_key(attr_name):
                widgetproxy.set_format(pre_formats[attr_name])
            if attr_name in pre_numeric:
                widgetproxy.set_numeric(True)
            if attr_name in pre_datetime:
                widgetproxy.set_datetime(True)

            # See Entry.SpinButtonProxy for details; numeric separators
            # bungle things up. Could be cleaned up by GNOME bug 
            # http://bugs.gnome.org/show_bug.cgi?id=114132
            if self._decimal_separator and isinstance(widget, gtk.SpinButton):
                widgetproxy.disable_numeric()

            self._set_proxy_vars(widgetproxy, attr_name)

        # Radiogroups need their own loop because they are composed of
        # multiple individual widgets
        for group_name, group in self._radiogroups.items():
            groupproxy = RadioGroup.RadioGroupProxy(self, group, group_name)
            self._set_proxy_vars(groupproxy, group_name)

    def _set_proxy_vars(self, proxy, name):
        proxy.default = proxy.read()
        self._attr_map[name] = proxy
        self._proxy_map[proxy] = name

    def _check_radiobutton(self, widget_name):
        radiogroups = getattr(self, "_radiogroups", None)
        if not radiogroups:
            raise AttributeError, ("No radiobutton groups have been "
                                   "defined. You *must* group *all* "
                                   "radiobuttons using group_radiobuttons() "
                                   "before calling __init__()")
        # build list of all grouped radiobuttons
        radiobuttons = []
        for group in radiogroups.keys():
            radiobuttons.extend(radiogroups[group].keys())
        if widget_name not in radiobuttons:
            raise AttributeError, \
                "Radiobutton '%s' is not a part of any group" % widget_name

    # Utility methods used by callbacks and setup methods

    def _get_widget_by_name(self, name):
        # When grabbing a widget from the UI, the attribute name may
        # contain dots (sub-attributes). We flatten out all dots into
        # underscores.
        name = string.replace(name, ".", "_")
        # We used to use get_widget here, but in the case of Glade UIs
        # it returns an unwrapped widget; we rely on wrapped widget to
        # detect Combo correctly, and I've settled for getattr() here.
        #
        # XXX: this will need to be changed for composition
        if not hasattr(self, name):
            raise ValueError, "The widget %s doesn't belong to %s" % \
                              (repr(name), self)
        return getattr(self, name)

    def _register_proxy_in_model(self, widget_name):
        model = self.model
        if not hasattr(model, "register_proxy_for_attribute"):
            return
        try:
            model.register_proxy_for_attribute(widget_name, self)
        except AttributeError:
            msg = ("Failed to run register_proxy() on Model %s "
                   "(that was supplied to  %s. \n"
                   "(Hint: if this model also inherits from ZODB's "
                   "Persistent class, this problem occurs if you haven't "
                   "set __setstate__() up correctly.  __setstate__() "
                   "should call Model.__init__() (and "
                   "Persistent.__setstate__() of course) to reinitialize "
                   "things properly.)")
            raise TypeError, msg % ( model, self )

    def _block_proxy_in_model(self, state):
        model = self.model
        if hasattr(model, "block_proxy"):
            if state:
                model.block_proxy(self)
            else:
                model.unblock_proxy(self)

    def _update_model(self, widgetproxy, value):
        if self.model is None:
            # skip updates for model if there is none, right?
            return

        attr_name = self._proxy_map.get(widgetproxy, None)
        if not attr_name:
            raise AssertionError, \
                "Couldn't find an attribute for widget %s" % widgetproxy.name

        if widgetproxy.converted:
            value = widgetproxy.read_converted(value)

        # XXX: one day we might want to queue and uniq updates?
        self._block_proxy_in_model(True)
        try:
            ksetattr(self.model, attr_name, value)
        except:
            if self._setter_error_handler:
                self._setter_error_handler(sys.exc_value, self.model, 
                                           attr_name, value)
            else:
                raise
        self._block_proxy_in_model(False)

        # Call global update hook 
        self.proxy_updated(widgetproxy, value)

#
# Concrete Classes
#

class SlaveProxy(SlaveDelegate, VirtualProxy):
    """
    The SlaveProxy class defines a proxy that has its interface built
    programatically, using PyGTK calls, and that is to be embedded in a
    View or Delegate by using attach_slave. See documentation for
    VirtualProxy for Proxy-related issues.
    """
    def __init__(self, model=None, toplevel=None, widgets=[]):
        """
        Creates a new SlaveProxy. Parameters:
            - model: the model instance to be attached to the proxy.
        """
        self.widgets = self._parse_widgets(widgets)
        # None of the Proxies pass in widgets to their parent
        # constructors because self.widgets is already set locally.
        SlaveView.__init__(self, toplevel)
        VirtualProxy.__init__(self, model)
        BaseController.__init__(self, view=self)
        self._VirtualProxy__initialize()

class GladeSlaveProxy(GladeSlaveDelegate, VirtualProxy):
    """
    The GladeSlaveProxy class defines a proxy that has its interface built
    from a Glade file. The contents of the container GtkWindow become the
    toplevel widgets, and it is to be embedded in a View or Delegate by
    using attach_slave. See documentation for VirtualProxy for Proxy-related
    issues."""
    def __init__(self, model=None, gladefile=None, container_name=None, 
                 widgets=[]):
        """
        Creates new GladeSlaveProxy:

            - model: the model instance to be attached to the proxy.
            - gladefile: the glade filename which holds the slave proxy. If not
              supplied, the class attribute will be checked for.
            - container_name: the name of the toplevel window in the glade file.
              If not supplied, the gladefile name will be used.
        """
        self.widgets = self._parse_widgets(widgets)
        GladeSlaveView.__init__(self, gladefile, container_name)
        VirtualProxy.__init__(self, model)
        BaseController.__init__(self, view=self)
        self._VirtualProxy__initialize()

class Proxy(Delegate, VirtualProxy):
    """
    The Proxy class defines a proxy that has its interface built
    programatically, using PyGTK calls. See documentation for
    VirtualProxy.
    """
    def __init__(self, model=None, toplevel=None, delete_handler=None, 
                 widgets=[]):

        """
        Creates a new Proxy. Parameters:
            - model: the model instance to be attached to the proxy.
            - toplevel and delete_handler are the same as for BaseView.__init__
        """
        self.widgets = self._parse_widgets(widgets)
        BaseView.__init__(self, toplevel, delete_handler)
        VirtualProxy.__init__(self, model)
        BaseController.__init__(self, view=self)
        self._VirtualProxy__initialize()

class GladeProxy(GladeDelegate, VirtualProxy):
    """
    GladeProxy is a proxy that uses a glade file as its interface
    definition. See documentation for VirtualProxy.
    """
    def __init__(self, model=None, gladefile=None, toplevel_name=None,
                 delete_handler=None, widgets=[]):
        """
        Creates a new GladeProxy. Parameters:

            - model: the instance to be attached to the proxy
            - gladefile: the glade file which contains the interface definition for
              this proxy
            - toplevel_name: the name of the toplevel widget this proxy will use;
              this widget name must be defined in the gladefile
            - delete_handler: a function to be called when the toplevel widget
              (IOW, window) is deleted
            - widgets: a list of widget names to be attached from glade to the proxy
              instance. You can also use self.widgets or a class attribute.

        See the documentation for GladeView if you are still confused.
        """
        # Make sure we have the right set of widgets
        self.widgets = self._parse_widgets(widgets)
        GladeView.__init__(self, gladefile, toplevel_name, delete_handler)
        VirtualProxy.__init__(self, model)
        BaseController.__init__(self, view=self)
        self._VirtualProxy__initialize()

