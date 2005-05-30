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
# Author(s): Lorenzo Gil Sanchez <lgs@sicem.biz>
#            Gustavo Rahal <gustavo@async.com.br>
#            Johan Dahlin <jdahlin@async.com.br>
#

from datetime import date
import locale
import time

__all__ = ['ValidationError', 'format', 'converter']

class ValidationError(Exception):
    pass

# by default locale uses the C locale but our date conversions use the user
# locale so we need to set the locale to that one
locale.setlocale(locale.LC_ALL, '') # this set the user locale ( $LANG )

def format(format, value):
    return locale.format(format, value, 1)

class ConverterRegistry:
    def __init__(self):
        self._converters = {}

    def add(self, converter_type):
        c = converter_type()
        self._converters[c.type] = c

    def get_supported_types(self):
        return self._converters.values()

    def get_supported_type_names(self):
        return [t.type.__name__ for t in self._converters.values()]

    def get_list(self):
        return self._converters.values()
    
    def to_string(self, converter_type, data, *args, **kwargs):
        c = self._converters[converter_type]
        if c.to_string is None:
            return data

        return c.to_string(data, *args, **kwargs)
            
    def from_string(self, converter_type, data, *args, **kwargs):
        c = self._converters[converter_type]
        if c.from_string is None:
            return data

        return c.from_string(data, *args, **kwargs)

# Global converter, can be accessed from outside
converter = ConverterRegistry()


class StringConverter:
    type = str
    
    as_string = None
    from_string = None
converter.add(StringConverter)

class IntConverter:
    type = int

    as_string = str

    def from_string(self, value):
        "Convert a string to an integer"
        try:
            return int(value)
        except ValueError:
            raise ValidationError("This field requires an integer number")
converter.add(IntConverter)
    
class BoolConverter:
    type = bool
    
    as_string = str

    def from_string(self, value, default_value=True):
        "Convert a string to a boolean"
        if value.upper() in ('TRUE', '1'):
            return True
        elif value.upper() in ('FALSE', '0'):
            return False
        else:
            return default_value
converter.add(BoolConverter)

class FloatConverter:
    type = float
    
    def __init__(self):
        self._locale_dictionary = locale.localeconv()
        
    def as_string(self, value):
        """Convert a float to a string"""
        return format('%f', value)

    def from_string(self, value):
        """Convert a string to a float"""
        th_sep = self._locale_dictionary["thousands_sep"]
        dec_sep = self._locale_dictionary["decimal_point"]
    
        # XXX: HACK! did this because lang like pt_BR and es_ES are
        #            considered to not have a thousand separator
        if th_sep == "":  
            th_sep = '.'

        th_sep_count = value.count(th_sep)
        dec_sep_count = value.count(dec_sep)
        if th_sep_count > 0 or dec_sep_count > 0:
            # we have separators
            if dec_sep_count > 1:
                raise ValidationError(
                    'You have more than one decimal separator ("%s") '
                    ' in your number "%s"' % (dec_sep, value))

            if th_sep_count > 0 and dec_sep_count > 0:
                # check if the dec separator is to right of every th separator
                dec_pos = value.index(dec_sep)
                th_pos = value.find(th_sep)
                while th_pos != -1:
                    if dec_pos < th_pos:
                        raise ValidationError(
                            "The decimal separator is to the left of "
                            "the thousand separator")
                    th_pos = value.find(th_sep, th_pos+1)
        value = value.replace(th_sep, '')
        value = value.replace(dec_sep, '.')
        try:
            return float(value)
        except ValueError:
            raise ValidationError("This field requires a number")
converter.add(FloatConverter)

class DateConverter:
    type = date
    
    def __init__(self):
        self._format = locale.nl_langinfo(locale.D_FMT)

        tmp = self._format[:]
        for code, replacement in (('%y', 'yy'),
                                  ('%Y', 'yyyy'),
                                  ('%m', 'mm'),
                                  ('%d', 'dd')):
            tmp = tmp.replace(code, replacement)
        self._readable_format = tmp
        
    def as_string(self, value):
        "Convert a date to a string"
        return value.strftime(self._format)
    
    def from_string(self, value):
        "Convert a string to a date"
        try:
            dateinfo = time.strptime(value, self._format)
            year, month, day = dateinfo[0:3]
            return date(year, month, day)
        except ValueError:
            raise ValidationError('This field requires a date of '
                                  'the format "%s"' % self._readable_format)
converter.add(DateConverter)

class ObjectConverter:
    type = object
    
    as_string = None
    from_string = None
converter.add(ObjectConverter)

