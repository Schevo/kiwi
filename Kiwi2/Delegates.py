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

from Kiwi2 import ValueUnset
from Kiwi2.Views import SlaveView, GladeView, GladeSlaveView, BaseView
from Kiwi2.List import List
from Kiwi2.initgtk import gtk
from Kiwi2.accessors import kgetattr
from Controllers import BaseController

class SlaveDelegate(SlaveView, BaseController):
    """A class that combines view and controller functionality into a
    single package. It does not possess a top-level window, but is instead
    intended to be plugged in to a View or Delegate using attach_slave().
    """
    def __init__(self, toplevel=None, widgets=[]):
        """Create new SlaveDelegate. toplevel is the toplevel widget,
        defaults to the value of the class' toplevel attribute, and if not
        present, raises AttributeError.
        """
        SlaveView.__init__(self, toplevel, widgets)
        BaseController.__init__(self, view=self)

class GladeSlaveDelegate(GladeSlaveView, BaseController):
    """A class that combines a controller and a GladeSlaveView. It is
    intended to be plugged into a View or Delegate using attach_slave().
    """
    def __init__(self, gladefile=None, container_name=None, widgets=[]):
        """Creates a new GladeSlaveDelegate. gladefile is the name of
        the Glade XML file, and container_name is the name of the toplevel
        GtkWindow that holds the slave.
        """
        GladeSlaveView.__init__(self, gladefile, container_name, widgets)
        BaseController.__init__(self, view=self)

class Delegate(BaseView, BaseController):
    """A class that combines view and controller functionality into a
    single package. The Delegate class possesses a top-level window.
    """
    def __init__(self, toplevel=None, delete_handler=None, widgets=[]):
        """Creates a new Delegate. For parameters , see BaseView.__init__"""
        BaseView.__init__(self, toplevel, delete_handler, widgets)
        BaseController.__init__(self, view=self)

class GladeDelegate(GladeView, BaseController):
    """A Delegate that uses a Glade file to specify its UI."""
    def __init__(self, gladefile=None, toplevel_name=None, 
                 delete_handler=None, widgets=[]):
        """Creates a new GladeDelegate. For parameters,
        see GladeView.__init__
        """
        GladeView.__init__(self, gladefile, toplevel_name, delete_handler, 
                           widgets)
        BaseController.__init__(self, view=self)

class ListDelegate(SlaveDelegate):
    """A View that builds a List around a specification for a class,
    and fills it with a list of instances for that class. It also provides
    an easy way to save and restore the column status (hidden/sorted/width)
    to allow persisting user settings.

    The ListDelegate defines one public attribute: list, which is the
    List widget it holds.
    """
    def __init__(self, columns, instance_list=None, mode=gtk.SELECTION_BROWSE):
        """Creates a new ListDelegate. Parameters:
            - columns specifies a list of Column instances, one for each column
            in the List. The Column defines how that particular column is
            to be displayed.

            If no Column has the `sorted' attribute set, we assume a normal,
            unsorted List is to be built; otherwise, a SortedList is
            created.  This has impact over the add_instance() method - for
            normal Lists, append() is called; for SortedList,
            insert_sorted().
            
            - instance_list offers a list of instances to be inserted into
            the list. If no list is provided, the List will be initialized
            empty, and the columns won't be autosized or aligned by type; the
            first add_list() is called, these will be set up appropriately.
            
            - mode is the selection mode the list is set to (defaulting nicely
            to SELECTION_BROWSE)
        """
        self.list = List(columns, instance_list, mode)

        # Set up pixmaps for creation of clist
        #title_pixmaps = {}
        #pixmap_specs = {}
        #for i in range(0, len(columns)):
            #column = columns[i]
            #title = column.title_pixmap
            #if title:
                #title_pixmaps[i] = find_in_gladepath(title)
            #pixmap_spec = column.pixmap_spec
            #if pixmap_spec:
                #pixmap_specs[i] = {}
                #for k,v in pixmap_spec.items():
                    #if v is None: # Avoid using gladepath for None pixmaps
                                  ## (see CList.__init__ docstring)
                        #pixmap_specs[i][k] = None
                    #else:
                        #pixmap_specs[i][k] = find_in_gladepath(v)

        date_formats = {}
        #if USE_MX:
            ## Put together date_formats
            #for i in range(len(columns)):
                #column = columns[i]
                #if column.type is DateTimeType and \
                   #column.format is not None:
                    #date_formats[i] = column.format

        self.list.show()

        SlaveDelegate.__init__(self, self.list)

    def __nonzero__(self):
        return 1

    def __getitem__(self, arg):
        return self.list[arg]
    
    def __len__(self):
        """Returns the number of instances in the list"""
        return len(self.list)

    def clear_list(self):
        """Clears the list of all items."""
        self.add_list(list=[], clear=True)

    def focus_toplevel(self):
        """Fixes up the default method to focus the list (and not the the
        scrolledwindow, which doesn't make a lot of sense"""
        self.list.grab_focus()

    def dump_columns(self):
        """
Returns a list of Column instances, each representing a column.  This
list can be saved and used to initialize the CList with the same
configuration as before."""
        ret = []
        columns = self._columns
        clist = self.clist
        for i in range(0, len(columns)):
            column = columns[i]
            column.width = clist.get_column_width(i)
            column.visible = clist.column_visibility[i]
            if i == clist.sort_column:
                column.sorted = True
                column.order = clist.sort_type
            else:
                column.sorted = False
                column.order = -1
            ret.append(column)
        return ret

    # XXX: This is busted. It doesn't work for type
    def dump_column_code(self):
        """Returns Python code that contains commands to instantiate a
set of Columns that reflect the current state of the Clist."""
        ret = self.dump_columns()
        text = ""
        for c in ret:
            # columns with pixmaps need specs declared beforehand; see
            # Column.dump_code().
            if c.pixmap_spec:
                name = "pixmap_spec_%s" % c.attribute
                text = text + "%s = %s\n" % (name, c.pixmap_spec)
        text = text + "columns = ["
        for c in ret:
            text = text + c.dump_code()
        return text + "\n]"

    def get_clist(self):
        """Returns the clist object the CListDelegate holds"""
        _warn("get_clist() is deprecated, use the `clist' attribute") 
        return self.clist

    def dump_list(self):
        """Returns a copy of the list of instances held by the CListDelegate"""
        return self._list[:]

    def dump_list_ordered(self):
        """Returns a copy of the list of instances held by the
        CListDelegate in the same order as it appears in the clist."""
        return map(lambda row: row['data'], self.clist.get_rows()) 

    def get_selected(self):
        """
Returns a tuple of the currently selected instances. A tuple is
necessary because in some CList modes (SELECTION_MULTIPLE and
SELECTION_EXTENDED) multiple rows might be selected simultaneously.
"""
        return self.list.get_selected()

    def set_selection_mode(self, mode=gtk.SELECTION_BROWSE):
        """
Changes the selection mode (the default being gtk.SELECTION_BROWSE).
The possible values for mode are: gtk.SELECTION_SINGLE,
gtk.SELECTION_BROWSE, gtk.SELECTION_MULTIPLE and gtk.SELECTION_EXTENDED.
"""
        self.clist.set_selection_mode(mode)

    def remove_instance(self, instance):
        """
Removes the instance from the clist. Raises KeyError if instance not in list.
"""
        clist = self.clist
        row = clist.find_row_from_data(instance)
        if row < 0:
            raise KeyError, "Instance %s not in list %s; it contains %s" \
                             % (instance, self, self._list)
        clist.remove(row)
        self._list.remove(instance)

    def select_instance(self, instance):
        """
Selects the row which displays the specified instance, raises KeyError
if instance not in list.
"""
        row = self.clist.find_row_from_data(instance)
        if row < 0:
            raise KeyError, "Instance %s not in list %s; it contains %s" \
                             % (instance, self, self._list)
        self._select_and_focus_row(row) 

    def update_instance(self, instance, select=False):
        """
Updates the text in the rows to the current state of the instance
provided. Raises KeyError if instance not in list.
"""
        clist = self.clist
        row = clist.find_row_from_data(instance)
        if row < 0:
            raise KeyError, "Instance %s not in list %s; it contains %s" \
                             % (instance, self, self._list)
        text = self._get_instance_text(instance)
        clist.set_row(row, text)
        if select:
            self._select_and_focus_row(row)

    def add_instance(self, instance, select=False):
        """
Adds an instance to the CListDelegate. If the CList is sorted (according
to the columns specified) insert_sorted() is used; otherwise, append()
is used.
    - instance: the instance to be added (according to the columns spec)
    - select: whether or not the new item should appear selected.
      See the docs for add_list() for a description of a bug that exists
      in versions of pygtk previous to 0.6.12.
"""
        clist = self.clist
        # Freeze and save original selection mode to avoid blinking
        clist.freeze()
        old_mode = clist['selection_mode']
        clist.set_selection_mode(gtk.SELECTION_SINGLE)
        
        if not self._typelist:
            self._typelist = self._get_types(instance, self._columns)
            clist.set_typelist(self._typelist)
            self._justify_columns(self._columns, self._typelist)

        # Now that the CList is ready, really add the instance
        row = self._real_add_instance(instance)

        # Avoid spurious selection or signal emissions when swapping
        # selection mode
        if self._handler_sig:
            clist.signal_handler_block(self._handler_sig)
        clist.set_selection_mode(old_mode)
        if self._handler_sig:
            clist.signal_handler_unblock(self._handler_sig)

        if select:
            self._select_and_focus_row(row)
        clist.thaw()
        return row

    def _real_add_instance(self, instance):
        # Implements actually adding the instance
        clist = self.clist
        text = self._get_instance_text(instance)
        if isinstance(clist, SortedCList):
            row = clist.insert_sorted(text, instance)
        else:
            row = clist.append(text)
            clist.set_row_data(row, instance)
        if self._autosize:
            clist.columns_autosize()
            # Don't reset _autosize, because one instance isn't enough
            # to make sure the CList looks good
        self._list.append(instance)
        return row

    def _get_instance_text(self, instance):
        # gets the text from the instance in the order specified in
        # self.columns
        columns = self._columns
        translate = string.translate
        text = []
        for c in columns:
            value = kgetattr(instance, c.attribute, ValueUnset)
            if value is ValueUnset:
                msg = "Failed to get attribute '%s' for %s"
                raise TypeError, msg % (c.attribute, instance)
            if value is None:
                value = ""
            elif type(value) is BooleanType:
                # We can't do str(True) directly because it turns into "True"
                value = str(int(value))
            elif c.format:
                try:
                    if USE_MX and c.data_type is DateTimeType:
                        # If we actually *got* a datetime object
                        if type(value) is DateTimeType:
                            value = value.strftime(c.format)
                        else:
                            # The value was already pre-converted
                            value = str(value)
                    else:                    
                        value = c.format % value
                except TypeError: 
                    raise TypeError, "Failed to convert %s to format %s" \
                                  % (repr(value), c.format)
            else:
                value = str(value)
            # Swap if special decimal_separator is set
            if c.type in (IntType, FloatType) and c.decimal_separator:
                trans = c.decimal_translator
                value = translate(value, trans)
            text.append(value)
        return text
    
    def _get_instance_attributes(self, instance):
        # gets the text from the instance in the order specified in
        # self.columns
        columns = self._columns
        attributes = []
        for c in columns:
            value = kgetattr(instance, c.attribute, ValueUnset)
            if value is ValueUnset:
                msg = "Failed to get attribute '%s' for %s"
                raise TypeError, msg % (c.attribute, instance)
            attributes.append(value)
        return tuple(attributes)


    def _load(self, l, progress_handler=None):
        if not l: # do nothing if empty list or None provided
            return

        columns = self._columns
        # typelist *may* be uncreated at this point: we do lazy creation
        # since we might not have a sample instance at instantiation
        # time. 
        if not self._typelist:
            self._typelist = self._get_types(l[0], columns)
            self.list.set_typelist(self._typelist)
            self._justify_columns(self._columns, self._typelist)

        # XXX XXX XXX XXX XXX XXX XXX
        # This is a fast, hacked-for-speed loop. We use internal list
        # methods to make sure it runs as fast as possible, doing all
        # non-variant processing out of the main loop.
        #column = self.list.sort_column
        #if list._decimal_hack.has_key(column):
            #decimal = list._decimal_hack[column]
        #else:
            #decimal = None
        #convert = list._get_column_converter(column)
    
        list_len = len(l)
        # Call progress handler a total of 50 times or less; the or
        # tricks just avoid a division by zero
        step = int(list_len/50) or 1
        if step == 1:
            # You can't have a step of 1, or else the progress handler
            # will never trigger (because n % 1 is always 0)
            step = 2
        i = 0

        #_get_text = self._get_instance_text
        #_get_row = list._locate_nearest_row
        #_insert = list._raw_insert
        #_set_row_data = clist.set_row_data
        #_o = clist._o
        _get_attributes = self._get_instance_attributes

        retval = list_len
        for item in l:
            #text = _get_text(item)
            #row = _get_row(text[column], column, decimal, convert=convert)
            #insert_row = _insert(_o, row, text)
            #_set_row_data(insert_row, item)
            self.list.append(_get_attributes(item))
            if progress_handler is None:
                continue
            i = i + 1
            if i % step: 
                percent = i / float(list_len)
                if progress_handler(percent):
                    # If the progress handler returns a true value, stop
                    # iterating at once and break.
                    retval = -1
                    l = list(l)[:i]
                    break
        else:
            if progress_handler:
                progress_handler(1)

        # Update list with the items we actually added
        self._list = self._list + list(l)

        # End speed-hack
        # XXX XXX XXX XXX XXX XXX XXX

        # As soon as we have data for that list, we can autosize it, and
        # we don't want to autosize again, or we may cancel user
        # modifications.
        if self._autosize:
            self.list.columns_autosize()
            self._autosize = False
        # This makes the column arrow show up when the list is visible
        # it works around the fact that the arrow never gets shown if
        # the list wasn't visible in the first place. It's a bit of a
        # hack, but hey, it works
        #gtk.idle_add(clist.update_column_arrow)
        return retval

    def _get_justify_by_type(self, tp):
        if tp in (int, float):
            just = gtk.JUSTIFY_RIGHT
#        elif USE_MX and tp is DateTimeType:
#            just = gtk.JUSTIFY_RIGHT
        else:
            just = gtk.JUSTIFY_LEFT
        return just

    def _justify_columns(self, columns, typelist):
        for i in range(0, len(columns)):
            column = columns[i]
            # Justification comes either from a column spec or from the
            # type list itself.
            justify = None
            if column.justify is not None:
                justify = column.justify
            elif typelist:
                justify = self._get_justify_by_type(typelist[i])
            # Apply to the column itself
            if justify is not None:
                self.clist.set_column_justification(i, justify)
                column.justify = justify

    def _select_and_focus_row(self, row):
        clist = self.clist
        mode = clist['selection_mode'] 
        clist.select_row(row, -1)
        if mode in (gtk.SELECTION_BROWSE, gtk.SELECTION_EXTENDED):
            if hasattr(clist, "set_focus_row"):
                clist.set_focus_row(row)
            else:
                _warn("Focus row bug, upgrade pygtk to 0.6.12")

        if not clist.row_is_visible(row):
            # We want to scroll the list to make sure the item is
            # visible. However, for some reason, if we are adding an
            # item to the last row of a long list, we *need* to use
            # idle_add or it won't scroll all the way.
            gtk.idle_add(clist.moveto, row, 0, 1.0, 0.0)

