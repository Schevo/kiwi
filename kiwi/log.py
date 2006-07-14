#
# Kiwi: a Framework and Enhanced Widgets for Python
#
# Copyright (C) 2005-2006 Async Open Source
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
# Author(s): Adriano Monteiro <adriano@globalret.com.br>
#            Johan Dahlin     <jdahlin@async.com.br>
#

import fnmatch
import logging
import os
import sys

class LogError(Exception):
    pass

class Formatter(logging.Formatter):
    def format(self, record):
        # 1: format
        # 2-6: logging module
        # 7: log (log.info/log.warn etc)
        # 8: callsite
        frame = sys._getframe(8)
        filename = os.path.basename(frame.f_code.co_filename)
        record.msg = '%s:%d %s' % (filename, frame.f_lineno, record.msg)
        return logging.Formatter.format(self, record)

class Logger(logging.Logger):
    log_domain = 'default'
    def __init__(self, name=None, level=logging.NOTSET):
        """Initializes Log module, creating log handler and defining log
        level. level attribute is not mandatory. It defines from which level
        messages should be logged. Logs with lower level are ignored.

        logging default levels table:

        Level
          - logging.NOTSET
          - logging.DEBUG
          - logging.INFO
          - logging.WARNING
          - logging.ERROR
          - logging.CRITICAL
        """
        if not name:
            name = Logger.log_name
        logging.Logger.__init__(self, name, get_log_level(name))

        stream_handler = logging.StreamHandler(sys.stdout)

        # Formater class define a format for the log messages been
        # logged with this handler
        # The following format string
        #   ("%(asctime)s (%(levelname)s) - %(message)s") will result
        # in a log message like this:
        #   2005-09-07 18:15:12,636 (WARNING) - (message!)
        format_string = ("%(asctime)s %(message)s")
        stream_handler.setFormatter(Formatter(format_string,
                                              datefmt='%T'))
        self.addHandler(stream_handler)

    def __call__(self, message, *args, **kwargs):
        self.info(message, *args, **kwargs)

_log_levels = {}
_default_level = logging.WARNING

def set_log_level(name, level):
    """
    @param name: logging category
    @param level: level
    """
    global _log_levels
    _log_levels[name] = level

def get_log_level(name):
    """
    @param name: logging category
    @returns: the level
    """
    global _log_levels, _default_level

    for category in _log_levels:
        if fnmatch.fnmatch(name, category):
            level = _log_levels[category]
            break
    else:
        level = _default_level
    return level

def _read_log_level():
    global _default_level

    log_levels = {}
    # bootstrap issue, cannot depend on environ
    log_level = os.environ.get('KIWI_LOG')
    if not log_level:
        return log_levels

    for part in log_level.split(','):
        if not ':' in part:
            continue

        if part.count(':') > 1:
            raise LogError("too many : in part %s" % part)
        name, level = part.split(':')
        try:
            level = int(level)
        except ValueError:
            raise LogError("invalid level: %s" % level)

        if level < 0 or level > 5:
            raise LogError("level must be between 0 and 5")

        level = 50 - (level * 10)

        if name == '*':
            _default_level = level
            continue
        log_levels[name] = level

    return log_levels

_log_levels = _read_log_level()

kiwi_log = Logger('kiwi')
