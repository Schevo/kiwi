#!/usr/bin/env python
#
# Kiwi: a Framework and Enhanced Widgets for Python
#
# Copyright (C) 2001,2002 Async Open Source
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
# Author(s): Lorenzo Gil Sanchez <lgs@sicem.biz>


from Kiwi2.accessors import kgetattr
from Kiwi2 import ValueUnset
from Kiwi2.initgtk import gtk, gobject

# Minimum number of rows where we show busy cursor when sorting numeric columns
MANY_ROWS = 1000

class Column:
    """Specifies a column in a List"""
    # put default values as class variables
    attribute = None
    title = None
    data_type = None
    visible = True
    justify = None
    format = None
    tooltip = None
    title_pixmap = None
    width = None
    sorted = False
    order = gtk.SORT_ASCENDING
    pixmap_spec = None
    decimal_separator = None
    def __init__(self, 
                 attribute     = None,
                 title         = None, 
                 data_type     = None,
                 visible       = None, 
                 justify       = None,
                 format        = None,
                 tooltip       = None,
                 title_pixmap  = None,
                 width         = None,
                 sorted        = None,
                 order         = None,
                 pixmap_spec   = None,
                 decimal_separator = None
                 ):
        """Creates a new Column, which describes how a column in a
        List should be rendered.
        - attribute: a string with the name of the instance attribute the
        column represents
        - title: the title of the column, defaulting to the capitalized form
        of the attribute
        - type: the type of the attribute that will be inserted into the
        column 
        - visible: a boolean specifying if it is initially hidden or shown
        - justify: one of gtk.JUSTIFY_LEFT, gtk.JUSTIFY_RIGHT or
        gtk.JUSTIFY_CENTER or None. If None, the justification will be
        determined by the type of the attribute value of the first
        instance to be inserted in the List (integers and floats
        will be right-aligned).
        - format: a format string to be applied to the attribute value upon
        insertion in the list
        - width: the width in pixels of the column, if not set, uses the
        default to List. If no Column specifies a width,
        columns_autosize() will be called on the List upon add_instance()
        or the first add_list().
        - sorted: whether or not the List is to be sorted by this column.
        If no Columns are sorted, the List will be created unsorted.
        - order: one of gtk.SORT_ASCENDING or gtk.SORT_DESCENDING or -1. The
        value -1 is used internally when the column is not sorted.
        - title_pixmap: if set to a filename (that can be in gladepath), a pixmap
        will be used *instead* of the title set. The title string will still be
        used to identify the column in the column selection and in a tooltip, if
        a tooltip is not set.
        """
        # XXX: filter function?
        if attribute is not None:
            self.attribute = attribute
        if not self.attribute:
            raise AttributeError, "Must supply an attribute"
        if title is not None:
            # XXX: this should *not* be stored as a typeobject or it ruins pickle
            self.title = title
        elif self.title is None:
            self.title = self.attribute.capitalize()
        if data_type is not None:
            self.data_type = data_type
        if visible is not None:
            self.visible = visible
        if justify is not None:
            self.justify = justify
        if format is not None:
            self.format = format
        if width is not None:
            self.width = width
        if sorted is not None:
            self.sorted = sorted
        if order is not None:
            self.order = order
        if title_pixmap is not None:
            self.title_pixmap = title_pixmap
        if self.title_pixmap: 
            # if title is a pixmap, we offer the title itself as tooltip
            # if a tip is not specifically set.
            self.tooltip = tooltip or self.title
        elif tooltip is not None:
            # set a tooltip when provided; we don't use the title
            # because it's silly to have identical tooltip and title 
            self.tooltip = tooltip
        if pixmap_spec is not None:
            self.pixmap_spec = pixmap_spec
        # Handle separators for specialized types
#        if self.type in (IntType, FloatType):
#            self.decimal_separator = (decimal_separator or 
#                                      self.decimal_separator or 
#                                      Views.global_decimal_separator)
#            self.ensure_decimal_translator()
        # XXX: validate bizarre option combinations
        # Tip: when adding items here, remember to update
        # CListDelegate.dump_column_code()

    def ensure_decimal_translator(self):
        sep = self.decimal_separator
        if sep:
            self.decimal_translator = string.maketrans(".%s" % sep, 
                                                        "%s." % sep)

    def dump_code(self):
        cdict = {}
        for name in dir(self):
            cdict[name] = getattr(self, name)
        cdict["attribute"] = repr(self.attribute)
        cdict["title"]  = repr(self.title)
        cdict["title_pixmap"]  = repr(self.title_pixmap)
        cdict["format"]  = repr(self.format)
        cdict["decimal_separator"]  = repr(self.decimal_separator)
        cdict["tooltip"] = repr(self.tooltip)
        if self.pixmap_spec:
            name = "pixmap_spec_%s" % self.attribute
            cdict["pixmap_spec"] = ", pixmap_spec=%s" % name
        else:
            cdict["pixmap_spec"] = ""
        # Isn't printing text lovely?
        return """
\tColumn(attribute=%(attribute)s, title=%(title)s, visible=%(visible)s, justify=%(justify)s, 
\t\tformat=%(format)s, tooltip=%(tooltip)s, width=%(width)s, sorted=%(sorted)s,
\t\torder=%(order)s, title_pixmap=%(title_pixmap)s%(pixmap_spec)s,
\t\tdecimal_separator=%(decimal_separator)s)""" % cdict

    def __repr__(self):
        dict = self.__dict__.copy()
        attr = dict['attribute']
        del dict['attribute']
        return "<%s %s: %s>" % (self.__class__.__name__, attr, dict)

class List(gtk.ScrolledWindow):
    """An enhanced version of GtkTreeView, which provides pythonic wrappers
    for accessing rows, and optional facilities for column sorting (with
    types) and column selection."""
    __gsignals__ = {
        'selection-change' : (gobject.SIGNAL_RUN_LAST, None, ()),
        'double-click' : (gobject.SIGNAL_RUN_LAST, None, (object,)),
        }
    
    def __init__(self, column_definitions,
                 instance_list=None,
                 mode=gtk.SELECTION_BROWSE):
        """Create a new Kiwi TreeView.
        """
        gtk.ScrolledWindow.__init__(self)
        # we always want a vertical scrollbar. Otherwise the button on top
        # of it doesn't make sense. This button is used to display the popup
        # menu
        self.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_ALWAYS)
        
        self._column_definitions = list(column_definitions)

        self.model = gtk.ListStore(object)
        self.model.set_sort_func(0, self._sort_function)
        self.treeview = gtk.TreeView(self.model)
        self.treeview.show()
        self.add(self.treeview)
        
        self.treeview.set_rules_hint(True)

        # these tooltips are used for the columns
        self._tooltips = gtk.Tooltips()

        # convinience connections
        id = self.treeview.get_selection().connect("changed",
                                                   self._on_selection__changed)
        self._selection_changed_id = id
        id = self.treeview.connect_after("row-activated",
                                         self._on_treeview__row_activated)
        self._row_activated_id = id

        # create a popup menu for showing or hiding columns
        self._popup = gtk.Menu()

        # get type information and crete the columns
        
        self._has_types_information = True
        # check if all the columns has the data_type set
        for col in self._column_definitions:
            if col.data_type is None:
                self._has_types_information = False
                break
            
        # if not, try to guess the data_types from the first instance
        if not self._has_types_information:
            if instance_list is not None:
                instance_list = tuple(instance_list)
                self._get_types(instance_list[0])
                self._has_types_information = True

        if self._has_types_information:
            self._create_columns()


        # by default we are unordered. This index points to the column
        # definition of the column that dictates the order, in case there is
        # any
        self._sort_column_definition = -1
        
        self._setup()

        if instance_list is not None:
            self.treeview.freeze_notify()
            self._load(instance_list)
            self.treeview.thaw_notify()

        if self._sort_column_definition_index != -1:
            cd = self._column_definitions[self._sort_column_definition_index]
            self.model.set_sort_column_id(0, cd.order)

        # Set selection mode last to avoid spurious events
        self.set_selection_mode(mode)

#        self.__setup_popup_button()

    def _setup(self):
        """Post initialize the List. This should be called everytime
        a critical component is changed (like a column definition).
        """
        # are we sorted?
        self._sort_column_definition_index = self._which_sort()
        i = self._sort_column_definition_index
        if i != -1:
            treeview_column = self.treeview.get_column(i)
            treeview_column.set_sort_indicator(True)

        # fine grain setup
        self._setup_columns()
        
    def _setup_columns(self):
        autosize = True
        for i, column in enumerate(self._column_definitions):
            treeview_column = self.treeview.get_column(i)
            treeview_column.connect("clicked", self._on_column__clicked, i)
            if column.width is not None:
                treeview_column.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
                treeview_column.set_fixed_width(column.width)
                autosize = False
            if column.tooltip is not None:
                widget = self.__get_column_button(treeview_column)
                if widget is not None:
                    self._tooltips.set_tip(widget, column.tooltip)
                    
#%s where I expected a GtkButton""" % (column.tooltip, i, col))
            #if column.decimal_separator:
            ## XXX: This is a hack. I now see we need to keep the data model
            ## in the CList too, but it's too late to add this. Anyway,
            ## call ensure to make sure the translator exists.
                #column.ensure_decimal_translator()
                #clist._fix_decimal_separator(i, column.decimal_translator)

        # typelist here may be none. It's okay; justify_columns will try
        # and use the specified justifications and if not present will
        # not touch the column. When typelist is not set,
        # add_instance/add_list have a chance to fix up the remaining
        # justification by looking at the first instance's data.
#        self._justify_columns(columns, typelist)

        self._autosize = autosize

        #clist.enable_column_select()

    # Columns handling
    def _get_types(self, instance):
        """Iterates through columns, using the type attribute when found or
        the type of the associated attribute from the sample instance provided.
        """
        for c in self._column_definitions:
            if c.data_type is not None:
                continue
            # steal attribute from sample instance and use its type
            value = kgetattr(instance, c.attribute, ValueUnset)
            if value is ValueUnset:
                msg = "Failed to get attribute '%s' for %s"
                raise TypeError, msg % (c.attribute, instance)
            
            tp = type(value)
            c.data_type = tp
            if tp is type(None):
                raise TypeError, \
                      """Detected invalid type None for column `%s'; please
                      specify type in Column constructor.""" % c.attribute

    def _create_columns(self):
        """Create the treeview columns"""
        for i, col in enumerate(self._column_definitions):
            treeview_column = gtk.TreeViewColumn()

            # we need to set our own widget because otherwise
            # __get_column_button won't work
            label = gtk.Label(col.title)
            label.show()
            treeview_column.set_widget(label)
            
            renderer = self._create_best_renderer_for_type(col.data_type, i)
            treeview_column.pack_start(renderer)
            treeview_column.set_cell_data_func(renderer, self._set_cell_data,
                                               col.attribute)
            self.treeview.append_column(treeview_column)
            treeview_column.set_visible(col.visible)
            treeview_column.set_resizable(True)
            treeview_column.set_clickable(True)
            treeview_column.set_reorderable(True)

            # add a menuitem in the popup
            menuitem = gtk.CheckMenuItem(col.title)
            menuitem.set_active(col.visible)
            menuitem.connect("activate", self._on_menuitem__activate,
                             treeview_column)
            menuitem.show()
            self._popup.append(menuitem)

            # setup the button to show the popup menu
            button = self.__get_column_button(treeview_column)
            button.connect('button-press-event',
                           self._on_header__button_press_event)
            
    def _create_best_renderer_for_type(self, data_type, column_index):
        """Create the best CellRenderer for a given type.
        It also set the property of the renderer that depends on the model,
        in the renderer.
        """
        if data_type in (int, float):
            renderer = gtk.CellRendererText()
            renderer.set_data('renderer-property', 'text')
            renderer.set_property('editable', True)
            renderer.connect('edited', self._on_renderer__edited, column_index)
        elif data_type is bool:
            renderer = gtk.CellRendererToggle()
            renderer.set_data('renderer-property', 'active')
            renderer.set_property('activatable', True)
            renderer.connect('toggled', self._on_renderer__toggled,
                             column_index)
        elif issubclass(data_type, basestring):
            renderer = gtk.CellRendererText()
            renderer.set_data('renderer-property', 'text')
            renderer.set_property('editable', True)
            renderer.connect('edited', self._on_renderer__edited, column_index)
        else:
            raise ValueError, "the type %s is not supported yet" % data_type
        
        return renderer

    def _set_cell_data(self, column, cellrenderer, model, iter,
                       model_attribute):
        """This method is called for every cell in the treeview that needs to
        be renderer. No need to say it has to be *fast*
        """
        renderer_prop = cellrenderer.get_data('renderer-property')
        instance = model.get_value(iter, 0)
        data = getattr(instance, model_attribute, None)
        cellrenderer.set_property(renderer_prop, data)

    def _on_header__button_press_event(self, button, event):
        if event.button == 3:
            self._popup.popup(None, None, None, event.button, event.time)
            return True

        return False

    def _on_menuitem__activate(self, menuitem, treeview_column):
        treeview_column.set_visible(menuitem.get_active())

    def _on_renderer__edited(self, renderer, path, new_text, column_index):
        row_iter = self.model.get_iter(path)
        instance = self.model.get_value(row_iter, 0)
        model_attribute = self._column_definitions[column_index].attribute
        data_type = self._column_definitions[column_index].data_type
        value = new_text
        if data_type in (int, float):
            value = data_type(new_text)
        # XXX convert new_text to the proper data type

        setattr(instance, model_attribute, value)
        
    def _on_renderer__toggled(self, renderer, path, column_index):
        row_iter = self.model.get_iter(path)
        instance = self.model.get_value(row_iter, 0)
        value = not renderer.get_active()
        model_attribute = self._column_definitions[column_index].attribute
        setattr(instance, model_attribute, value)
        
    # selection methods
    def _find_iter_from_data(self, instance):
        data_iter = self.model.get_iter_first()
        while data_iter:
            if instance == self.model.get_value(data_iter, 0):
                break
            data_iter = self.mode.iter_next()
        return data_iter

    def _select_and_focus_row(self, row_iter):
        self.treeview.set_cursor(self.model.get_path(row_iter))
                    
    # sorting methods
    def _which_sort(self):
        """Return the index of the first column with the sorted attribute
        set to True.
        """
        for i, c in enumerate(self._column_definitions):
            if c.sorted:
                return i
        return -1

    def _sort_function(self, model, iter1, iter2):
        obj1 = model.get_value(iter1, 0)
        obj2 = model.get_value(iter2, 0)
        cd = self._column_definitions[self._sort_column_definition_index]
        attr = cd.attribute
        value1 = getattr(obj1, attr)
        value2 = getattr(obj2, attr)
        return cmp(value1, value2)

    def _on_column__clicked(self, treeview_column, column_index):
        if self._sort_column_definition_index == -1:
            # this mean we are not sorting at all
            return

        old_column = self.treeview.get_column(self._sort_column_definition_index)
        old_column.set_sort_indicator(False)
        
        # reverse the old order or start with SORT_DESCENDING if there was no
        # previous order
        self._sort_column_definition_index = column_index
        cd = self._column_definitions[column_index]

        # maybe it's the first time this column is ordered
        if cd.order is None:
            cd.order = gtk.SORT_DESCENDING

        # reverse the order
        old_order = cd.order
        if old_order == gtk.SORT_ASCENDING:
            new_order = gtk.SORT_DESCENDING
        else:
            new_order = gtk.SORT_ASCENDING
        cd.order = new_order

        # cosmetic changes
        treeview_column.set_sort_indicator(True)
        treeview_column.set_sort_order(new_order)

        # This performs the actual ordering
        self.model.set_sort_column_id(0, new_order)

    # handlers
    def _on_selection__changed(self, selection):
        self.emit('selection-change')

    def _on_treeview__row_activated(self, treeview, path, view_column):
        row_iter = self.model.get_iter(path)
        selected_obj = self.model.get_value(row_iter, 0)
        self.emit('double-click', selected_obj)
        
    # Python virtual methods
    def __getitem__(self, arg):
        if isinstance(arg, int):
            item = self.model[arg][0]
        elif isinstance(arg, gtk.TreeIter):
            item = self.model.get_value(arg, 0)
        else:
            raise ValueError, "the index is not an intenger neither a iter"
        
        return item

    def __setitem__(self, arg, item):
        if isinstance(arg, int):
            self.model[arg] = (item,)
        elif isinstance(arg, gtk.TreeIter):
            self.model.set_value(arg, 0, item)
        else:
            raise ValueError, "the index is not an intenger neither a iter"
            
    def __len__(self):
        return len(self.model)

    def _load(self, instance_list):
        if not instance_list: # do nothing if empty list or None provided
            return

        for instance in instance_list:
            self.model.append((instance,))
            
        # As soon as we have data for that list, we can autosize it, and
        # we don't want to autosize again, or we may cancel user
        # modifications.
        if self._autosize:
            self.treeview.columns_autosize()
            self._autosize = False

    # hacks
    def __get_column_button(self, column):
        """Return the button widget of a particular TreeViewColumn.

        This hack is needed since that widget is private of the TreeView but
        we need access to them for Tooltips, right click menus, ...

        Use this function at your own risk
        """
        button = column.get_widget()
        assert button is not None, "You must call column.set_widget() before calling __get_column_button"
        while not isinstance(button, gtk.Button):
            button = button.get_parent()

        return button

    # start of the hack to put a button on top of the vertical scrollbar
    def __setup_popup_button(self):
        """Put a button on top of the vertical scrollbar to show the popup
        menu.
        Internally it uses a POPUP window so you can tell how *Evil* is this.
        """
        self.__popup_window = gtk.Window(gtk.WINDOW_POPUP)
        self.__popup_button = gtk.Button('*')
        self.__popup_window.add(self.__popup_button)
        self.__popup_window.show_all()
        
        self.forall(self.__find_vertical_scrollbar)
        self.connect('size-allocate', self._on_scrolled_window__size_allocate)
        self.connect('realize', self._on_scrolled_window__realize)

    def __find_vertical_scrollbar(self, widget):
        """This method is called from a .forall() method in the ScrolledWindow.
        It just save a reference to the vertical scrollbar for doing evil
        things later.
        """
        if isinstance(widget, gtk.VScrollbar):
            self.__vscrollbar = widget


    def __get_header_height(self):
        treeview_column = self.treeview.get_column(0)
        button = self.__get_column_button(treeview_column)
        alloc = button.get_allocation()
        return alloc.height

    def _on_scrolled_window__realize(self, widget):
        toplevel = widget.get_toplevel()
        self.__popup_window.set_transient_for(toplevel)
        self.__popup_window.set_destroy_with_parent(True)
        
    def _on_scrolled_window__size_allocate(self, widget, allocation):
        """Resize the Vertical Scrollbar to make it smaller and let space
        for the popup button. Also put that button there.
        """
        old_alloc = self.__vscrollbar.get_allocation()
        height = self.__get_header_height()
        new_alloc = gtk.gdk.Rectangle(old_alloc.x, old_alloc.y + height,
                                      old_alloc.width,
                                      old_alloc.height - height)
        self.__vscrollbar.size_allocate(new_alloc)
        # put the popup_window in its position
        gdk_window = self.window
        if gdk_window is not None:
            x, y = gdk_window.get_origin()
            self.__popup_window.move(x + old_alloc.x, y + old_alloc.y)
        
    # end of the popup button hack
    
    #
    # Public API
    #
    def add_instance(self, instance, select=False):
        """Adds an instance to the list.
        - instance: the instance to be added (according to the columns spec)
        - select: whether or not the new item should appear selected.
        """
        # Freeze and save original selection mode to avoid blinking
        self.treeview.freeze_notify()
        old_mode = self.get_selection_mode()
        self.set_selection_mode(gtk.SELECTION_SINGLE)
        
##         if not self._typelist:
##             self._typelist = self._get_types(instance, self._column_definitions)
##             clist.set_typelist(self._typelist)
##             self._justify_columns(self._column_definitions, self._typelist)

        row_iter = self.model.append((instance,))
        if self._autosize:
            self.treeview.columns_autosize()

        # Avoid spurious selection or signal emissions when swapping
        # selection mode
        selection = self.treeview.get_selection()
        selection.handler_block(self._selection_changed_id)
        self.set_selection_mode(old_mode)
        selection.handler_unblock(self._selection_changed_id)

        if select:
            self._select_and_focus_row(row_iter)
        self.treeview.thaw_notify()

    def set_column_visibility(self, column_index, visibility):
        self.treeview.get_column(column_index).set_visible(visibility)

    def get_selection_mode(self):
        return self.treeview.get_selection().get_mode()
    
    def set_selection_mode(self, mode):
        self.treeview.get_selection().set_mode(mode)

    def unselect_all(self):
        self.treeview.get_selection().unselect_all()
        
    def get_selected(self):
        selection = self.treeview.get_selection()
        model, paths = selection.get_selected_rows()
        if paths:
            result = [model.get_value(model.get_iter(p), 0) for p in paths]
            return tuple(result)

    def add_list(self, list, clear=True, restore_selection=False,
                 progress_handler=None):
        """Allows a list to be loaded, by default clearing it first.
        freeze() and thaw() are called internally to avoid flashing.
        - list: a list to be added
        - clear: a boolean that specifies whether or not to clear the list
        - restore_selection: a boolean that specifies whether or not to
        try and preserve the original selection in the list (provided that
        at least some instances are still present in the new list.)
        - progress_handler: a callback function to be called while the list
        is being filled

        There is a problem with select=True and mode SELECTION_BROWSE. The
        focus_row is not updated, and the end result is that you have a
        row selected but another row focused, which is a serious bug. I
        have implemented a workaround for this in pygtk-0.6.12.
        """
        # change mode to selection single to avoid generating spurious
        # select_row signals. yes, we could do this using emit_stop_by_name 
        # and then emit, but I think this is easier on the eyes
        self.treeview.freeze_notify()
        old_mode = self.get_selection_mode()
        old_sel = self.get_selected()
        self.set_selection_mode(gtk.SELECTION_SINGLE)
        if clear:
            self.unselect_all()
            self.model.clear()

        ret = self._load(list, progress_handler)

        # Avoid spurious selection or signal emissions when swapping
        # selection mode
        self.treeview.handler_block(self._selection_changed_id)
        self.set_selection_mode(old_mode)
        self.treeview.handler_unblock(self._selection_changed_id)

        if restore_selection:
            for instance in old_sel:
                # we need to find the rows because some instances may
                # have disappeared with the clear/_load
                row_iter = self._find_iter_from_data(instance)
                if row_iter is not None:
                    self._select_and_focus_row(row_iter)
        elif (old_mode in (gtk.SELECTION_BROWSE, gtk.SELECTION_EXTENDED)
              and clear):
            # If the mode was browse, and we cleared the list, we need
            # to make sure that at least one selection signal is
            # emitted, or applications might end up with inconsistent
            # state.
            row_iter = self.model.get_iter_first()
            self._select_and_focus_row(row_iter)
            
        self.treeview.thaw_notify()
        return ret

gobject.type_register(List)

if __name__ == '__main__':
    win = gtk.Window()
    win.set_default_size(300, 150)
    win.connect('destroy', gtk.main_quit)

    class Person:
        def __init__(self, name, age, city, single):
            self.name, self.age, self.city, self.single = name, age, city, single

    columns = (
        Column('name', sorted=True, tooltip='What about a stupid tooltip?'),
        Column('age'),
        Column('city', visible=True),
        Column('single', title='Single?')
        )
    
    data = (Person('Evandro', 23, 'Belo Horizonte', False),
            Person('Daniel', 22, 'Sao Carlos', False),
            Person('Henrique', 21, 'Sao Carlos', True),
            Person('Gustavo', 23, 'San Jose do Santos', True),
            Person('Johan', 23, 'Goteborg', True), 
            Person('Lorenzo', 26, 'Granada', True)
        )

    l = List(columns, data)

    # add an extra person
    l.add_instance(Person('Nando', 29, 'Santos', False))

    win.add(l)
    win.show_all()
    
    gtk.main()
