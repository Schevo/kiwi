from datetime import date

# by default locale uses the C locale but our date conversions use the user
# locale so we need to set the locale to that one
import locale
locale.setlocale(locale.LC_ALL, '') # this set the user locale ( $LANG )

import time

date_format = locale.nl_langinfo(locale.D_FMT)

def set_date_format(format):
    """Set the format for date conversions.

    format is a string suitable for the date.strftime function like %d/%m/%y
    By default format is the user locale date format and if the format argument
    is None it revert to this one."""
    global date_format
    if format is None:
        date_format = locale.nl_langinfo(locale.D_FMT)
    else:
        if not isinstance(format, str):
            raise TypeError("Format should be a string, found a %s" % \
                            type(format))
        date_format = format
    
def str2date(value):
    "Convert a string to a date"
    global date_format
    dateinfo = time.strptime(value, date_format)
    year, month, day = dateinfo[0:3]
    return date(year, month, day)

def date2str(value):
    "Convert a date to a string"
    global date_format
    return value.strftime(date_format)

def str2bool(value, default_value=True):
    "Convert a string to a boolean"
    if value.upper() in ('TRUE', '1'):
        return True
    elif value.upper() in ('FALSE', '0'):
        return False
    else:
        return default_value
    
supported_types = (str, int, float, bool, date)

supported_types_names = map(lambda t: t.__name__, supported_types)

TO_STR, FROM_STR = range(2)

converters = {
    TO_STR:   {
        str: lambda v: v,
        int: str,
        float: str,
        bool: str,
        date: date2str,
        },
    FROM_STR: {
        str: lambda v: v,
        int: int,
        float: float,
        bool: str2bool,
        date: str2date,
        }
    }

default_values = {
    str: '',
    int: 0,
    float: 0.0,
    bool: True,
    date: None,
    }
