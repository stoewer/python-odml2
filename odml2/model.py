# coding=UTF-8

# Copyright (c) 2015, Adrian Stoewer (adrian.stoewer@rz.ifi.lmu.de)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the project.

__all__ = ("Section", "Value", "value_from")

import re
import datetime as dt
import numbers
import odml2
from odml2 import compat

PLUS_MINUS_UNICODE = u"±"
PLUS_MINUS = PLUS_MINUS_UNICODE if compat.PY3 else "+-"


class Section(object):
    """
    Represents an odML section entity.
    """

    def __init__(self, uuid, back_end):
        self.__uuid = uuid
        self.__back_end = back_end

    @property
    def uuid(self):
        return self.__uuid

    @property
    def type(self):
        return self.__back_end.section_get_type(self.uuid)

    # noinspection PyMethodOverriding
    @type.setter
    def type(self, typ):
        self.__back_end.section_set_type(self.uuid, typ)

    @property
    def label(self):
        return self.__back_end.section_get_label(self.uuid)

    # noinspection PyMethodOverriding
    @label.setter
    def label(self, label):
        self.__back_end.section_set_label(self.uuid, label)

    @property
    def reference(self):
        return self.__back_end.section_get_reference(self.uuid)

    # noinspection PyMethodOverriding
    @reference.setter
    def reference(self, reference):
        self.__back_end.section_set_reference(self.uuid, reference)

    #
    # dict like access to sections and values
    #

    def items(self):
        for key in self.__back_end.section_get_properties(self.uuid):
            yield (key, self.get(key))

    def keys(self):
        for key in self.__back_end.section_get_properties(self.uuid):
            yield key

    def get(self, key):
        if self.__back_end.property_has_sections(self.uuid, key):
            return self.__back_end.property_get_sections(self.uuid, key)
        elif self.__back_end.property_has_value(self.uuid, key):
            return self.__back_end.property_get_value()

    def __len__(self):
        return len(self.__back_end.section_get_properties(self.uuid))

    def __iter__(self):
        return self.keys()

    def __getitem__(self, key):
        element = self.get(key)
        if element is None:
            raise KeyError("Key '%s' not in section with uuid '%s'" % (key, self.uuid))
        return element

    def __setitem__(self, key, element):
        # TODO handle list of Section and SB
        if isinstance(element, odml2.SB):
            element.build(self.__back_end, self.uuid, key)
        if isinstance(element, Section):
            # TODO implement setting a section as subsection
            raise NotImplementedError()
        else:
            val = value_from(element)
            self.__back_end.property_set_value(self.uuid, key, val)

    def __delitem__(self, key):
        self.__back_end.property_remove(self.uuid, key)

    #
    # built in methods
    #

    def __eq__(self, other):
        if isinstance(other, Section):
            return self.uuid == other.uuid
        else:
            return False

    def __str__(self):
        return "Section(type=%s, uuid=%s, label=%s)" % (self.type, self.uuid, self.label)

    def __repr__(self):
        return str(self)

    def __unicode__(self):
        return compat.unicode(str(self))


class Value(object):
    """
    An odML Value class
    """

    def __init__(self, value, unit=None, uncertainty=None):
        self.__value = value
        self.__unit = unit
        self.__uncertainty = uncertainty

    @property
    def value(self):
        return self.__value

    @property
    def unit(self):
        return self.__unit

    @property
    def uncertainty(self):
        return self.__uncertainty

    def using(self, value=None, unit=None, uncertainty=None):
        return Value(
            value if value is not None else self.value,
            unit if unit is not None else self.unit,
            uncertainty if uncertainty is not None else self.uncertainty
        )

    def __eq__(self, other):
        if isinstance(other, Value):
            return self.value == other.value and self.unit == other.unit and self.uncertainty == other.uncertainty
        else:
            return False

    @property
    def __value_str(self):
        if isinstance(self.value, (dt.date, dt.time, dt.datetime)):
            return self.value.isoformat()
        elif isinstance(self.value, (compat.unicode, str)):
            return self.value
        else:
            return str(self.value)

    def __str__(self):
        parts = [self.__value_str]
        if self.unit is not None:
            parts.append(self.unit)
        if self.uncertainty is not None:
            parts.append(PLUS_MINUS)
            parts.append(str(self.uncertainty))
        return str().join(parts)

    def __unicode__(self):
        parts = [self.__value_str]
        if self.unit is not None:
            parts.append(self.unit)
        if self.uncertainty is not None:
            parts.append(PLUS_MINUS_UNICODE)
            parts.append(str(self.uncertainty))
        return compat.unicode().join(parts)

    def __repr__(self):
        return str(self)

ALLOWED_VALUE_TYPES = (
    bool, int, float, numbers.Number, dt.date, dt.time, dt.datetime)
VALUE_EXPR = re.compile(
    u"^([-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?)" +
    "([A-Za-z]{1,2})?" +
    "((\+-|\\xb1)([0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?))?$")

def value_from(thing):
    if isinstance(thing, (str, compat.unicode)):
        match = VALUE_EXPR.match()
        if match is None:
            return Value(thing)
        else:
            groups = match.groups()
            return Value(float(groups[0]), str(groups[2]), float(groups[5]))
    if isinstance(thing, ALLOWED_VALUE_TYPES):
        return Value(thing)
    elif isinstance(thing, Value):
        return thing
    else:
        raise ValueError("Can't covert '%s' to a value" % repr(thing))
