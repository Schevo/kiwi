from datetime import date

class ValidationError(Exception):
    pass

# by default locale uses the C locale but our date conversions use the user
# locale so we need to set the locale to that one
import locale
locale.setlocale(locale.LC_ALL, '') # this set the user locale ( $LANG )

import time

date_format = locale.nl_langinfo(locale.D_FMT)
locale_dictionary = locale.localeconv()

def get_readable_format():
    global date_format
    table = {'%y': 'yy',
             '%Y': 'yyyy',
             '%m': 'mm',
             '%d': 'dd'}
    tmp = date_format
    for code in table.keys():
        tmp = tmp.replace(code, table[code])
    return tmp

readable_format = get_readable_format()

def set_date_format(format):
    """Set the format for date conversions.

    format is a string suitable for the date.strftime function like %d/%m/%y
    By default format is the user locale date format and if the format argument
    is None it revert to this one."""
    global date_format, readable_format
    if format is None:
        date_format = locale.nl_langinfo(locale.D_FMT)
    else:
        if not isinstance(format, str):
            raise TypeError("Format should be a string, found a %s" % \
                            type(format))
        date_format = format
        readable_format = get_readable_format()
    
def str2date(value):
    "Convert a string to a date"
    global date_format, readable_format
    try:
        dateinfo = time.strptime(value, date_format)
        year, month, day = dateinfo[0:3]
        return date(year, month, day)
    except ValueError:
        raise ValidationError('This field requires a date of the format "%s"' % readable_format)
    
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
    """Convert a string to a float"""
    
    th_sep = locale_dictionary["thousands_sep"]
    dec_sep = locale_dictionary["decimal_point"]
    if th_sep == ',':
        current_locale = 'comp'
    else:
        current_locale = 'other'
        # XXX: HACK! did this because lang like pt_BR and es_ES are considered to not have a thousand separator
        th_sep = '.'
    
    if value.count(th_sep) == 0 and value.count(dec_sep) == 0: # no separators
        pass
    
    else:
        if value.count(',') > 1 or value.count('.') > 1:
            raise ValidationError('Thousand separator is supposed to be a "%s" and '
                                      'decimal separator a "%s"'%(th_sep, dec_sep))
        
        sep_order = value.count(',') - value.count('.')
        comma_pos = value.find(',')
        dot_pos = value.find('.')
        
        # two separators
        if sep_order == 0:
            # comma is the first_sep?
            if comma_pos < dot_pos: # 
            #comp format
                if current_locale != 'comp':
                    raise ValidationError('Thousand separator is supposed to be a "%s" and '
                                      'decimal separator a "%s"'%(th_sep, dec_sep))
                else: #comp
                    value = value.replace(",", "")
                    
                    
            else:
            # other format             
                if current_locale != 'other':
                    raise ValidationError('Thousand separator is supposed to be a "%s" and '
                                      'decimal separator a "%s"'%(th_sep, dec_sep))
                else:
                    # fix the number 
                    value = value.replace('.', '')
                    value = value.replace(',', '.')

        # one separator                      
        else:
            if sep_order > 0: # comma is the sep
                if current_locale == 'other':
                    value = value.replace(",", ".")
                else: # comp
                    value = value.replace(",", "")
            else: # dot is the sep
                if current_locale == 'other':
                    value = value.replace(".", '')
                pass
                                
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
        float: locale.str,
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
