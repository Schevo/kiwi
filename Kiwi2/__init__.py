#
# Kiwi: a Framework and Enhanced Widgets for Python
#
# Copyright (C) 2003-2005 Async Open Source
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
#            Lorenzo Gil Sanchez <lgs@sicem.biz>
#            Johan Dahlin <jdahlin@async.com.br>
#         

"""Kiwi is a library designed to make developing graphical applications as easy as possible. It offers both a framework and a set of enhanced widgets, and is based on Python and GTK+. Kiwi borrows concepts from MVC, Java Swing and Microsoft MFC, but implements a set of unique classes that take advantage of the flexibility and simplicity of Python to make real-world application creation much easier.

Kiwi includes a Framework and a set of enhanced widgets, including CList, OptionMenu, Label, CTree, Entry and more.

    - Author: Christian Reis <kiko@async.com.br>
    - Website: U{http://www.async.com.br/projects/kiwi/}
    - Organization: Async Open Source
"""            

import os
import string
import sys

class ValueUnset:
    """To differentiate from places where None is a valid default. Used
    mainly in the Kiwi Proxy"""
    pass

from Kiwi2.version import version
kiwi_version = version

# Kiwi Combo, GtkRadioButton are non-standard and are handled specially
# inside AbstractProxy


def _warn(msg):
    sys.stderr.write("Kiwi warning: "+msg+"\n")

gladepath = []

if os.environ.has_key('KIWI_GLADE_PATH'):
    gladepath = os.environ['KIWI_GLADE_PATH'].split(':')

def set_gladepath(path):
    """Sets a new path to be used to search for glade files when creating
    GladeViews or it's subclasses
    """
    global gladepath
    gladepath = path

def get_gladepath():
    global gladepath
    return gladepath


imagepath = ''

if os.environ.has_key ('KIWI_IMAGE_PATH'):
    imagepath = string.split(os.environ['KIWI_IMAGE_PATH'])

def set_imagepath(path):
    global imagepath
    imagepath = path

def get_imagepath():
    global imagepath
    return imagepath
