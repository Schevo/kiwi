from datetime import date

class ValidationError(Exception):
    pass

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
    try:
        dateinfo = time.strptime(value, date_format)
        year, month, day = dateinfo[0:3]
        return date(year, month, day)
    except ValueError:
        raise ValidationError("This field requires a date")
    
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

def str2int(value):
    "Convert a string to an integer"
    try:
        return int(value)
    except ValueError:
        raise ValidationError("This field requires an integer number")

def str2float(value):
    "Convert a string to a float"
    try:
        return float(value)
    except ValueError:
        raise ValidationError("This field requires a number")
    
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
        int: str2int,
        float: str2float,
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
