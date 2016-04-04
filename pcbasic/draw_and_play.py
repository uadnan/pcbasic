"""
PC-BASIC - draw_and_play.py
DRAW and PLAY macro language stream utilities

(c) 2013, 2014, 2015, 2016 Rob Hagemans
This file is released under the GNU GPL version 3 or later.
"""

import string

import error
import vartypes
import operators
import representation
import util
import var
import memory
import state

# generic for both macro languages
ml_whitepace = ' '

def ml_parse_value(gmls, default):
    """ Parse a value in a macro-language string. """
    c = util.skip(gmls, ml_whitepace)
    sgn = -1 if c == '-' else 1
    if c in ('+', '-'):
        gmls.read(1)
        c = util.peek(gmls)
        # don't allow default if sign is given
        default = None
    if c == '=':
        gmls.read(1)
        c = util.peek(gmls)
        if len(c) == 0:
            raise error.RunError(error.IFC)
        elif ord(c) > 8:
            name = util.parse_scalar(gmls)
            indices = _ml_parse_indices(gmls)
            step = state.session.memory.get_variable(name, indices)
            util.require_read(gmls, (';',), err=error.IFC)
        else:
            # varptr$
            step = state.session.memory.get_value_for_varptrstr(gmls.read(3))
    elif c and c in string.digits:
        step = _ml_parse_const(gmls)
    elif default is not None:
        step = default
    else:
        raise error.RunError(error.IFC)
    if sgn == -1:
        step = operators.number_neg(step)
    return step

def ml_parse_number(gmls, default=None):
    """ Parse and return a number value in a macro-language string. """
    return vartypes.pass_int_unpack(ml_parse_value(gmls, default), err=error.IFC)

def ml_parse_string(gmls):
    """ Parse a string value in a macro-language string. """
    c = util.skip(gmls, ml_whitepace)
    if len(c) == 0:
        raise error.RunError(error.IFC)
    elif ord(c) > 8:
        name = util.parse_scalar(gmls, err=error.IFC)
        indices = _ml_parse_indices(gmls)
        sub = state.session.memory.get_variable(name, indices)
        util.require_read(gmls, (';',), err=error.IFC)
        return state.session.strings.copy(vartypes.pass_string(sub, err=error.IFC))
    else:
        # varptr$
        return state.session.strings.copy(
                vartypes.pass_string(
                    state.session.memory.get_value_for_varptrstr(gmls.read(3))))

def _ml_parse_const(gmls):
    """ Parse and return a constant value in a macro-language string. """
    c = util.skip(gmls, ml_whitepace)
    if c and c in string.digits:
        numstr = ''
        while c and c in string.digits:
            gmls.read(1)
            numstr += c
            c = util.skip(gmls, ml_whitepace)
        return vartypes.int_to_integer_signed(int(numstr))
    else:
        raise error.RunError(error.IFC)

def _ml_parse_const_int(gmls):
    """ Parse a constant value in a macro-language string, return Python int. """
    return vartypes.pass_int_unpack(_ml_parse_const(gmls), err=error.IFC)

def _ml_parse_indices(gmls):
    """ Parse constant array indices. """
    indices = []
    c = util.skip(gmls, ml_whitepace)
    if c in ('[', '('):
        gmls.read(1)
        while True:
            indices.append(_ml_parse_const_int(gmls))
            c = util.skip(gmls, ml_whitepace)
            if c == ',':
                gmls.read(1)
            else:
                break
        util.require_read(gmls, (']', ')'))
    return indices
