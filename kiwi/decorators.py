#
# Kiwi: a Framework and Enhanced Widgets for Python
#
# Copyright (C) 2005 Async Open Source
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
# Author(s): Johan Dahlin <jdahlin@async.com.br>
#

"""Function and method decorators used in kiwi"""

import gobject

from kiwi import _warn

class deprecated(object):
    """
    I am a decorator which prints a deprecation warning each
    time you call the decorated (and deprecated) function
    """
    def __init__(self, new):
        """
        @param new: the name of the new function replacing the old
          deprecated one
        @type new: string
        """
        self._new = new

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            _warn("%s is deprecated, use %s instead" % (func.__name__,
                                                        self._new))
            return func(*args, **kwargs)
        wrapper.__name__ = func.__name__
        return wrapper

class delayed(object):
    """
    I am a decorator which delays the function call using the gobject/gtk
    mainloop for a number of ms.
    """
    def __init__(self, delay):
        """
        @param delay: delay in ms
        @type delay:  integer
        """
        
        self._delay = delay
        self._timeout_id = -1

    def __call__(self, func):
        def real_call(args, kwargs):
            func(*args, **kwargs)
            self._timeout_id = -1
            return False
        
        def wrapper(*args, **kwargs):
            # Only one call at a time
            if self._timeout_id != -1:
                return
        
            self._timeout_id = gobject.timeout_add(self._delay,
                                                   real_call, args, kwargs)
        wrapper.__name__ = func.__name__
        return wrapper

        
class signal_block(object):
    """
    A decorator to be used on L{kiwi.ui.views.SlaveView} methods.
    It takes a list of arguments which is the name of the widget and
    the signal name separated by a dot.

    For instance:

        >>> class MyView(SlaveView):
        ...     @signal_block('money.changed')
        ...     def update_money(self):
        ...         self.money.set_value(10)
        ...     def on_money__changed(self):
        ...         pass


    When calling update_money() the value of the spinbutton called money
    will be updated, but on_money__changed will not be called.
    """
    
    def __init__(self, *signals):
        self.signals = []
        for signal in signals:
            if not isinstance(signal, str):
                raise TypeError("signals must be a list of strings")
            if signal.count('.') != 1:
                raise TypeError("signal must have exactly one dot")
            self.signals.append(signal.split('.'))

    def __call__(self, func):
        def wrapper(view, *args, **kwargs):
            for name, signal in self.signals:
                widget = getattr(view, name, None)
                if widget is None:
                    raise TypeError("Unknown widget %s in view " % name)
                view.handler_block(widget, signal)
                
            retval = func(view, *args, **kwargs)
            
            for name, signal in self.signals:
                widget = getattr(view, name, None)
                view.handler_unblock(widget, signal)
                
            return retval
        wrapper.__name__ = func.__name__
        return wrapper
