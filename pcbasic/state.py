"""
PC-BASIC - state.py
Support for pickling emulator state

(c) 2014, 2015, 2016 Rob Hagemans
This file is released under the GNU GPL version 3 or later.
"""

try:
    import cPickle as pickle
except ImportError:
    import pickle
try:
    import cStringIO
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
import copy_reg
import os
import logging
import zlib
import sys


def unpickle_file(name, mode, pos):
    """Unpickle a file object."""
    if name is None:
        if mode in ('r', 'rb'):
            return sys.stdin
        else:
            return sys.stdout
    try:
        if 'w' in mode and pos > 0:
            # preserve existing contents of writable file
            with open(name, 'rb') as f:
                buf = f.read(pos)
            f = open(name, mode)
            f.write(buf)
        else:
            f = open(name, mode)
            if pos > 0:
                f.seek(pos)
    except IOError:
        logging.warning('Could not re-open file %s. Replacing with null file.', name)
        f = open(os.devnull, mode)
    return f

def pickle_file(f):
    """Pickle a file object."""
    if f in (sys.stdout, sys.stdin):
        return unpickle_file, (None, f.mode, -1)
    try:
        return unpickle_file, (f.name, f.mode, f.tell())
    except IOError:
        # not seekable
        return unpickle_file, (f.name, f.mode, -1)

def unpickle_StringIO(value, pos):
    """Unpickle a cStringIO object."""
    # needs to be called without arguments or it's a StringI object without write()
    csio = StringIO()
    csio.write(value)
    csio.seek(pos)
    return csio

def pickle_StringIO(csio):
    """Pickle a cStringIO object."""
    value = csio.getvalue()
    pos = csio.tell()
    return unpickle_StringIO, (value, pos)

# register the picklers for file and cStringIO
copy_reg.pickle(file, pickle_file)
copy_reg.pickle(cStringIO.OutputType, pickle_StringIO)


def zunpickle(state_file):
    """Read a compressed pickle string."""
    if state_file:
        try:
            with open(state_file, 'rb') as f:
                return pickle.loads(zlib.decompress(f.read()))
        except EnvironmentError:
            logging.error('Could not read from %s', state_file)

def zpickle(obj, state_file):
    """Retuen a compressed pickle string."""
    if state_file:
        try:
            with open(state_file, 'wb') as f:
                f.write(zlib.compress(pickle.dumps(obj, 2)))
        except EnvironmentError:
            logging.error('Could not write to %s', state_file)
