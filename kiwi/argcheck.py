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

"""
Argument checking decorator and support
"""

import inspect

class CustomType(type):
    def value_check(cls, name, value):
        pass
    value_check = classmethod(value_check) 

class number(CustomType):
    """
    Custom type that verifies that the type is a number (eg float or int)
    """
    type = int, float
    
class percent(CustomType):
    """
    Custom type that verifies that the value is a percentage
    """
    type = int, float
    def value_check(cls, name, value):
        if 0 > value < 100:
            raise ValueError("%s must be between 0 and 100" % name)
    value_check = classmethod(value_check) 
       
class argcheck(object):
    """
    Decorator to check type and value of arguments.

    Usage:

        >>> @argcheck(types...)
        ... def function(args..)

    or

        >>> class Class:
        ...     @argcheck(types..)
        ...     def method(self, args)
        
    You can customize the checks by subclassing your type from CustomType,
    there are two builtin types: number which is a float/int combined check
    and a percent which verifis that the value is a percentage
    """
    
    __enabled__ = True
    
    def __init__(self, *types):
        for argtype in types:
            if not isinstance(argtype, type):
                raise TypeError("must be a type instance")
        self.types = types

    def enable(cls):
        """
        Enable argcheck globally
        """
        cls.__enabled__ = True
    enable = classmethod(enable)
    
    def disable(cls):
        """
        Disable argcheck globally
        """
        cls.__enabled__ = False
    disable = classmethod(disable)
        
    def __call__(self, func):
        if not callable(func):
            raise TypeError("%r must be callable" % func)

        spec = inspect.getargspec(func)
        arg_names, is_varargs, is_kwargs, default_values = spec
        
        # TODO: Is there another way of doing this?
        #       Not trivial since func is not attached to the class at
        #       this point. Nor is the class attached to the namespace.
        if arg_names and arg_names[0] in ('self', 'cls'):
            arg_names = arg_names[1:]
            is_method = True
        else:
            is_method = False
            
        types = self.types
        if is_kwargs and not is_varargs and self.types:
            raise TypeError("argcheck cannot be used with only keywords")
        elif not is_varargs:
            if len(types) != len(arg_names):
                raise TypeError("%s has wrong number of arguments, "
                                "%d specified in decorator, "
                                "but function has %d" %
                                (func.__name__,
                                 len(types),
                                 len(arg_names)))

        defs = len(default_values or ())
        kwarg_types = {}
        for i, arg_name in enumerate(arg_names):
            kwarg_types[arg_name] = types[i]
            
            pos = defs - i
            if defs and 0 < pos < defs:
                value = default_values[pos]
                arg_type = types[pos]
                try:
                    self._type_check(value, arg_type, arg_name)
                except TypeError:
                    raise TypeError("default value for %s must be of type %s "
                                    "and not %s" % (arg_name,
                                                    arg_type.__name__,
                                                    type(value).__name__))
        def wrapper(*args, **kwargs):
            if self.__enabled__:
                cargs = args
                if is_method:
                    cargs = cargs[1:]
                
                # Positional arguments
                for arg, type, name in zip(cargs, types, arg_names):
                    self._type_check(arg, type, name)

                # Keyword arguments
                for name, arg in kwargs.items():
                    self._type_check(arg, kwarg_types[name], name)
                
            return func(*args, **kwargs)
        wrapper.__name__ = func.__name__
        return wrapper

    def _type_check(self, value, argument_type, name):
        if issubclass(argument_type, CustomType):
            custom = True
            check_type = argument_type.type
        else:
            custom = False
            check_type = argument_type
            
        type_name = argument_type.__name__

        if not isinstance(value, check_type):
            raise TypeError(
                "%s must be %s, not %s" % (name, type_name,
                                           type(value).__name__))
        if custom:
            argument_type.value_check(name, value)


def test():
    @argcheck(int)
    def function(number):
        pass

    class Class:
        @argcheck(percent)
        def method(self, value):
            pass
        
    function(1)
    try:
        function(None) # fails
    except TypeError, e:
        print e
        
    o = Class()
    o.method(10.4) # works
    try:
        o.method(-1) # fails
    except ValueError, e:
        print e
    
if __name__ == '__main__':
    test()
