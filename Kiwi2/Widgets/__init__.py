def str2bool(value, default_value=True):
    if value.upper() in ('TRUE', '1'):
        return True
    elif value.upper() in ('FALSE', '0'):
        return False
    else:
        return default_value

supported_types = (str, int, float, bool)

supported_types_names = map(lambda t: t.__name__, supported_types)

TO_STR, FROM_STR = range(2)

converters = {
    TO_STR:   {
        'str': lambda v: v,
        'int': str,
        'float': str,
        'bool': str,
        },
    FROM_STR: {
        'str': lambda v: v,
        'int': int,
        'float': float,
        'bool': str2bool,
        }
    }

default_values = {
    'str': '',
    'int': 0,
    'float': 0.0,
    'bool': True,
    }

from List import List
from Entry import Entry
from Label import Label
from ComboBox import ComboBox, ComboBoxEntry
