#
# Kiwi: a Framework and Enhanced Widgets for Python
#
# Copyright (C) 2005,2006 Async Open Source
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
# Author(s): Johan Dahlin <jdahlin@async.com.br
#

"""
Test script playback system and infrastructure.
"""
import os
import sys
import threading
import time
import traceback

import gobject
gobject.threads_init()
import gtk
from gtk import gdk
gdk.threads_init()

from kiwi.log import Logger
from kiwi.ui.test.common import Base

WINDOW_TIMEOUT = 10
WINDOW_WAIT = 0.5
WIDGET_TIMEOUT = 2

# This is pretty important, it gives the application 2 seconds
# to finish closing the dialog, eg write stuff to the database and
# yada yada
DELETE_WINDOW_WAIT = 4

log = Logger('player')

_mainloop = None

class TimeOutError(Exception):
    """
    Exception that will be raised when a widget cannot be found,
    which will happen after a few seconds depending on the type
    of widget
    """
    pass

class ThreadSafeFunction:
    """
    A function which is safe thread in the mainloop context
    All widgets and object functions will be wrapped by this.
    """

    def __init__(self, func, obj_name):
        self._func = func
        self._obj_name = obj_name

    def _invoke(self, *args, **kwargs):
        gdk.threads_enter()
        log('Calling %s.%s(%s)' % (self._obj_name,
                                   self._func.__name__,
                                   ', '.join(map(repr, args))))
        self._func(*args, **kwargs)
        gdk.threads_leave()
        return False

    def __call__(self, *args, **kwargs):
        # dialog.run locks us out
        #rv = self._func(*args, **kwargs)
        gobject.idle_add(self._invoke, *args, **kwargs)

class ThreadSafeObject:
    """
    A wrapper around a gobject which replaces all callable
    objects which wraps all callable objects uses L{ThreadSafeFunction}.
    """
    def __init__(self, gobj):
        """
        @param gobj:
        """
        self._gobj = gobj

    def __getattr__(self, name):
        attr = getattr(self._gobj, name, None)
        if attr is None:
            raise KeyError(name)
        if callable(attr):
            return ThreadSafeFunction(attr, self._gobj.get_name())
        return attr

class DictWrapper(object):
    def __init__(self, dict, name):
        self._dict = dict
        self._name = name

    def __getattr__(self, attr):
        start = time.time()
        while True:
            if (time.time() - start) > WIDGET_TIMEOUT:
                raise TimeOutError("no %s called %s" % (self._name, attr))

            if attr in self._dict:
                return ThreadSafeObject(self._dict[attr])

            time.sleep(0.1)

class App(DictWrapper):
    def __init__(self, player):
        self._player = player

    def __getattr__(self, attr):
        return DictWrapper(self._player.get_object(attr), 'widget')

class Player(Base):
    """
    Event playback object. Usually called from inside a scripted generated by
    L{kiwi.ui.test.recorder.Recorder}.

    The application script will be exectured in a different thread,
    so to be able to conveniently use it a number of tricks are used
    to avoid making the user worry about threadsafety.
    """
    def __init__(self, args):
        """
        @param args:
        """
        Base.__init__(self)

        self._app = App(self)

        if not os.path.exists(args[0]):
            print >> sys.stderr, \
                  "ERROR: %s: No such a file or directory" % args[0]
            os._exit(1)

        # Send notification to main thread
        gobject.idle_add(self._start_app, args)

    def _start_app(self, args):
        log("Executing %s %s" % (args[0], args[1:]))
        sys.argv = args[:]
        execfile(sys.argv[0], globals(), globals())

        # Run all pending events, such as idle adds
        while gtk.events_pending():
            gtk.main_iteration()

    def get_app(self):
        """
        Returns a virtual application object, which is a special object
        where you can access the windows as attributes and widget in the
        windows as attributes on the window, examples:

        >>> app = player.get_app()
        >>> app.WindowName.WidgetName.method()

        @return: virtual application object
        """
        return self._app

    def wait_for_window(self, name, timeout=WINDOW_TIMEOUT):
        """
        Waits for a window with name I{name} to appear.

        @param name: the name of the window to wait for
        @param timeout: number of seconds to wait after the window appeared.
        """

        log('waiting for %s (%d)' % (name, timeout))

        # XXX: No polling!
        start_time = time.time()
        while True:
            if name in self._objects:
                window = self.get_object(name)
                time.sleep(WINDOW_WAIT)
                return window

            if time.time() - start_time > timeout:
                raise TimeOutError("could not find window %s" % name)
            time.sleep(0.05)

    def delete_window(self, window_name):
        """
        Deletes a window, creates a delete-event and sends it to the window
        """

        log('deleting window %s' % window_name)

        if window_name in self._objects:
            del self._objects[window_name]

        start_time = time.time()
        while True:
            window = self._windows.get(window_name)
            # If the window is already removed, skip
            if (not window_name in self._windows or
                window is None or
                window.window is None):
                return False

            if time.time() - start_time > DELETE_WINDOW_WAIT:
                event = gdk.Event(gdk.DELETE)
                event.window = window.window
                event.put()
                return True
            time.sleep(0.1)

    def finish(self):
        log("Player finished")
        global _mainloop
        _mainloop.quit()

def _player_excepthook(exc_type, exc_value, tb):
    traceback.print_exception(exc_type, exc_value, tb.tb_next)
    os._exit(1)

def play_file(filename, args=None):
    """
    Plays a recorded script file

    @param filename: name to play
    @param args: additional arguments to put in sys.argv
    """

    sys.excepthook = _player_excepthook

    if not os.path.exists(filename):
        raise SystemExit("%s: No such a file or directory" % filename)

    if not args:
        args = []

    sys.argv = [filename] + args

    def _thread(filename):
        try:
            execfile(filename)
        except:
            import traceback
            etype, value, tb = sys.exc_info()
            traceback.print_exception(etype, value, tb.tb_next)
            os._exit(1)

    log("Starting script thread")
    t = threading.Thread(target=_thread, args=[filename])
    t.start()

    log("Entering main loop")
    global _mainloop
    _mainloop = gobject.MainLoop()
    _mainloop.run()
    log("Leaving main loop")
