import sys
import gobject
import gtk

def gsignal(name, *args, **kwargs):
    """
    Add a GObject signal to the current object.
    @type name:   string
    @type args:   types
    @type kwargs: keyword argument 'flags' and/or 'retval'
    """

    frame = sys._getframe(1)
    try:
        locals = frame.f_locals
    finally:
        del frame
        
    if not '__gsignals__' in locals:
        dict = locals['__gsignals__'] = {}
    else:
        dict = locals['__gsignals__']

    if args and args[0] == 'override':
        dict[name] = 'override'
    else:
        flags = kwargs.get('flags', gobject.SIGNAL_RUN_FIRST)
        retval = kwargs.get('retval', None)
    
        dict[name] = (flags, retval, args)

def gproperty(name, type, default=None, nick=None,
              flags=gobject.PARAM_READWRITE):
    """
    Add a GObject property to the current object.
    @type type:    type
    @type default: default value
    @type name:    string
    @type nick:    string
    @type flags:   a gobject.ParamFlag
    """

    frame = sys._getframe(1)
    try:
        locals = frame.f_locals
    finally:
        del frame
        
    if not '__gproperties__' in locals:
        dict = locals['__gproperties__'] = {}
    else:
        dict = locals['__gproperties__']

    if nick is None:
        nick = name

    if default is None:
        if type == str:
            default = ''
        elif type == int:
            default = 0
        elif type == float:
            default = 0.0
        elif type == bool:
            default = true
            
    dict[name] = (type, name, nick, default, flags)

#
# Color control
#
def gdk_color_to_string(color):
    """Convert a color to a #AABBCC string"""
    # the values are in the 0-65535 range and we want 0-255
    red = color.red >> 8
    green = color.green >> 8
    blue = color.blue >> 8
    return "#%02X%02X%02X" % (red, green, blue)

def set_foreground(widget, color, state=gtk.STATE_NORMAL):
    """Set the foreground color of a widget:

    - widget: the widget we are changing the color
    - color: a hexadecimal code or a well known color name
    - state: the state we are afecting, see gtk.STATE_*
    """
    widget.modify_fg(state, gtk.gdk.color_parse(color))

def get_foreground(widget, state=gtk.STATE_NORMAL):
    """Return the foreground color of the widget as a string"""    
    style = widget.get_style()
    color = style.fg[state]
    return gdk_color_to_string(color)

def set_background(widget, color, state=gtk.STATE_NORMAL):
    """Set the background color of a widget:

    - widget: the widget we are changing the color
    - color: a hexadecimal code or a well known color name
    - state: the state we are afecting, see gtk.STATE_*
    """
    widget.modify_bg(state, gtk.gdk.color_parse(color))

def get_background(widget, state=gtk.STATE_NORMAL):
    """Return the background color of the widget as a string"""
    style = widget.get_style()
    color = style.bg[state]
    return gdk_color_to_string(color)
    
