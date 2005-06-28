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
#            Lorenzo Gil Sanchez <lgs@sicem.biz>
#            Johan Dahlin <jdahlin@async.com.br>
#

import os

from kiwi import get_gladepath, get_imagepath

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

class AbstractGladeAdaptor(object):
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

