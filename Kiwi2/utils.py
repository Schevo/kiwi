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
            default = True
            
    dict[name] = (type, name, nick, default, flags)

#
# Color control
#
def gdk_color_to_string(color):
    """Convert a color to a #AABBCC string"""
    return rgb_color_to_string(color.red, color.green, color.blue)

def rgb_color_to_string(red, green, blue):
    """Red green and blue should be in the 0-65535 range"""
    return "#%02X%02X%02X" % (red >> 8, green >> 8, blue >> 8)
    
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
    if isinstance(widget, gtk.Entry):
        widget.modify_base(state, gtk.gdk.color_parse(color))
    else:
        widget.modify_bg(state, gtk.gdk.color_parse(color))

def get_background(widget, state=gtk.STATE_NORMAL):
    """Return the background color of the widget as a string"""
    style = widget.get_style()
    color = style.bg[state]
    return gdk_color_to_string(color)
    

def merge_colors(widget, src_color, dst_color, steps=10):
    """Change the background of widget from src_color to dst_color
    in the number of steps specified
    """
    gdk_src = gtk.gdk.color_parse(src_color)
    gdk_dst = gtk.gdk.color_parse(dst_color)
    rs, gs, bs = gdk_src.red, gdk_src.green, gdk_src.blue
    rd, gd, bd = gdk_dst.red, gdk_dst.green, gdk_dst.blue
    rinc = (rd - rs) / float(steps)
    ginc = (gd - gs) / float(steps)
    binc = (bd - bs) / float(steps)
    for i in xrange(steps):
        rs += rinc
        gs += ginc
        bs += binc
        color = rgb_color_to_string(int(rs), int(gs), int(bs))
        set_background(widget, color)
        yield True

    yield False
