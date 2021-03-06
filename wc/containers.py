# -*- coding: iso-8859-1 -*-
# Copyright (C) 2004-2010 Bastian Kleineidam
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
"""
Special container classes.
"""

class AttrDict(dict):
    """Dictionary allowing attribute access to its elements if they
    are valid attribute names and not already existing methods."""

    def __getattr__(self, name):
        return self[name]


class ListDict(dict):
    """A dictionary whose iterators reflect the order in which elements
    were added.
    """

    def __init__(self):
        """Initialize sorted key list."""
        super(ListDict, self).__init__()
        # sorted list of keys
        self._keys = []

    def setdefault(self, key, *args):
        if key not in self:
            self._keys.append(key)
        return super(ListDict, self).setdefault(key, *args)

    def __setitem__(self, key, value):
        """Add key,value to dict, append key to sorted list."""
        if key not in self:
            self._keys.append(key)
        super(ListDict, self).__setitem__(key, value)

    def __delitem__(self, key):
        """Remove key from dict."""
        self._keys.remove(key)
        super(ListDict, self).__delitem__(key)

    def pop(self, key):
        if key in self._keys:
            self._keys.remove(key)
        super(ListDict, self).pop(key)

    def popitem(self):
        if self._keys:
            k = self._keys[0]
            v = self[k]
            del self[k]
            return (k, v)
        raise KeyError("popitem() on empty dictionary")

    def values(self):
        """Return sorted list of values."""
        return [self[k] for k in self._keys]

    def items(self):
        """Return sorted list of items."""
        return [(k, self[k]) for k in self._keys]

    def keys(self):
        """Return sorted list of keys."""
        return self._keys[:]

    def itervalues(self):
        """Return iterator over sorted values."""
        for k in self._keys:
            yield self[k]

    def iteritems(self):
        """Return iterator over sorted items."""
        for k in self._keys:
            yield (k, self[k])

    def iterkeys(self):
        """Return iterator over sorted keys."""
        return iter(self._keys)

    def clear(self):
        """Remove all dict entries."""
        self._keys = []
        super(ListDict, self).clear()

    def get_true(self, key, default):
        """Return default element if key is not in the dict, or if self[key]
        evaluates to False. Useful for example if value is None, but
        default value should be an empty string.
        """
        if key not in self or not self[key]:
            return default
        return self[key]


class CaselessDict(dict):
    """A dictionary ignoring the case of keys (which must be strings)."""

    def __getitem__(self, key):
        assert isinstance(key, basestring)
        return dict.__getitem__(self, key.lower())

    def __delitem__(self, key):
        assert isinstance(key, basestring)
        return dict.__delitem__(self, key.lower())

    def __setitem__(self, key, value):
        assert isinstance(key, basestring)
        dict.__setitem__(self, key.lower(), value)

    def __contains__(self, key):
        assert isinstance(key, basestring)
        return dict.__contains__(self, key.lower())

    def get(self, key, def_val=None):
        assert isinstance(key, basestring)
        return dict.get(self, key.lower(), def_val)

    def setdefault(self, key, *args):
        assert isinstance(key, basestring)
        return dict.setdefault(self, key.lower(), *args)

    def update(self, other):
        for k, v in other.items():
            dict.__setitem__(self, k.lower(), v)

    def fromkeys(cls, iterable, value=None):
        d = cls()
        for k in iterable:
            dict.__setitem__(d, k.lower(), value)
        return d
    fromkeys = classmethod(fromkeys)

    def pop(self, key, *args):
        assert isinstance(key, basestring)
        return dict.pop(self, key.lower(), *args)


class CaselessSortedDict(CaselessDict):
    """Caseless dictionary with sorted keys."""

    def keys(self):
        return sorted(super(CaselessSortedDict, self).keys())

    def items(self):
        return [(x, self[x]) for x in self.keys()]

    def iteritems(self):
        return ((x, self[x]) for x in self.keys())


class LFUCache(dict):
    """Limited cache which purges least frequently used items."""

    def __init__(self, size=1000):
        super(LFUCache, self).__init__()
        if size < 1:
            raise ValueError("invalid cache size %d" % size)
        self.size = size

    def __setitem__(self, key, val):
        """Store given key/value."""
        if key in self:
            # store value with existing number of uses
            num_used = self[key][0]
            super(LFUCache, self).__setitem__(key, [num_used, val])
        else:
            super(LFUCache, self).__setitem__(key, [0, val])
            # check for size limit
            if len(self) > self.size:
                self.shrink()

    def shrink(self):
        """Shrink ca. 5% of entries."""
        trim = int(0.95*len(self))
        if trim:
            items = super(LFUCache, self).items()
            values = sorted([(value, key) for key, value in items])
            for value, key in values[0:trim]:
                del self[key]

    def __getitem__(self, key):
        value = super(LFUCache, self).__getitem__(key)
        value[0] += 1
        return value[1]

    def uses(self, key):
        """Get number of uses for given key (without increasing the number of
        uses)"""
        return super(LFUCache, self).__getitem__(key)[0]

    def get(self, key, def_val=None):
        if key in self:
            return self[key]
        return def_val

    def setdefault(self, key, def_val=None):
        if key in self:
            return self[key]
        self[key] = def_val
        return def_val

    def items(self):
        return [(key, value[1]) for key, value in super(LFUCache, self).items()]

    def iteritems(self):
        for key, value in super(LFUCache, self).iteritems():
            yield (key, value[1])

    def values(self):
        return [value[1] for value in super(LFUCache, self).values()]

    def itervalues(self):
        for value in super(LFUCache, self).itervalues():
            yield value[1]

    def popitem(self):
        key, value = super(LFUCache, self).popitem()
        return (key, value[1])

    def pop(self):
        value = super(LFUCache, self).pop()
        return value[1]


try:
    from collections import namedtuple
except ImportError:
    from keyword import iskeyword as _iskeyword
    from operator import itemgetter as _itemgetter
    import sys

    def namedtuple(typename, field_names, verbose=False):
        # Parse and validate the field names.  Validation serves two purposes,
        # generating informative error messages and preventing template injection attacks.
        if isinstance(field_names, basestring):
            field_names = field_names.replace(',', ' ').split() # names separated by whitespace and/or commas
        field_names = tuple(field_names)
        for name in (typename,) + field_names:
            if not all(c.isalnum() or c=='_' for c in name):
                raise ValueError('Type names and field names can only contain alphanumeric characters and underscores: %r' % name)
            if _iskeyword(name):
                raise ValueError('Type names and field names cannot be a keyword: %r' % name)
            if name[0].isdigit():
                raise ValueError('Type names and field names cannot start with a number: %r' % name)
        seen_names = set()
        for name in field_names:
            if name.startswith('_'):
                raise ValueError('Field names cannot start with an underscore: %r' % name)
            if name in seen_names:
                raise ValueError('Encountered duplicate field name: %r' % name)
            seen_names.add(name)

        # Create and fill-in the class template
        numfields = len(field_names)
        argtxt = repr(field_names).replace("'", "")[1:-1]   # tuple repr without parens or quotes
        reprtxt = ', '.join('%s=%%r' % name for name in field_names)
        dicttxt = ', '.join('%r: t[%d]' % (name, pos) for pos, name in enumerate(field_names))
        template = '''class %(typename)s(tuple):
        '%(typename)s(%(argtxt)s)' \n
        __slots__ = () \n
        _fields = %(field_names)r \n
        def __new__(cls, %(argtxt)s):
            return tuple.__new__(cls, (%(argtxt)s)) \n
        @classmethod
        def _make(cls, iterable, new=tuple.__new__, len=len):
            'Make a new %(typename)s object from a sequence or iterable'
            result = new(cls, iterable)
            if len(result) != %(numfields)d:
                raise TypeError('Expected %(numfields)d arguments, got %%d' %% len(result))
            return result \n
        def __repr__(self):
            return '%(typename)s(%(reprtxt)s)' %% self \n
        def _asdict(t):
            'Return a new dict which maps field names to their values'
            return {%(dicttxt)s} \n
        def _replace(self, **kwds):
            'Return a new %(typename)s object replacing specified fields with new values'
            result = self._make(map(kwds.pop, %(field_names)r, self))
            if kwds:
                raise ValueError('Got unexpected field names: %%r' %% kwds.keys())
            return result \n\n''' % locals()
        for i, name in enumerate(field_names):
            template += '        %s = property(itemgetter(%d))\n' % (name, i)
        if verbose:
            print template
        # Execute the template string in a temporary namespace
        namespace = dict(itemgetter=_itemgetter)
        try:
            exec template in namespace
        except SyntaxError, e:
            raise SyntaxError(e.message + ':\n' + template)
        result = namespace[typename]
        # For pickling to work, the __module__ variable needs to be set to the frame
        # where the named tuple is created.  Bypass this step in enviroments where
        # sys._getframe is not defined (Jython for example).
        if hasattr(sys, '_getframe'):
            result.__module__ = sys._getframe(1).f_globals['__name__']
        return result


def enum(*names):
    """Return an enum datatype instance from given list of keyword names.
    The enum values are zero-based integers.

    >>> Status = enum('open', 'pending', 'closed')
    >>> Status.open
    0
    >>> Status.pending
    1
    >>> Status.closed
    2
    """
    return namedtuple('Enum', ' '.join(names))(*range(len(names)))
