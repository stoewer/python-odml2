# coding=UTF-8

# Copyright (c) 2015, Adrian Stoewer (adrian.stoewer@rz.ifi.lmu.de)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the project.

from uuid import uuid4

import odml2
from odml2.checks import *

__all__ = ("SB", )


class SB(object):
    """
    A section builder
    """

    # noinspection PyShadowingBuiltins
    def __init__(self, type, uuid=None, label=None, reference=None, **properties):
        uuid = str(uuid) if uuid is not None else str(uuid4())
        assert_name(type)
        assert_uuid(uuid)
        for p in properties:
            assert_name(p)
        self.type = type
        self.uuid = uuid
        self.label = label
        self.reference = reference
        self.properties = properties

    def build(self, back_end, parent_uuid=None, parent_prop=None):
        # TODO What about error handling (undo already built sections)?
        if parent_uuid is None:
            back_end.create_root(self.type, self.uuid, self.label, self.reference)
        else:
            if parent_prop is None:
                raise ValueError("A property name is needed in order to append a sub section")
            back_end.sections.add(self.type, self.uuid, self.label, self.reference, parent_uuid, parent_prop)

        for p, thing in self.properties.items():
            if isinstance(thing, (list, tuple)):
                for sub in thing:
                    if isinstance(sub, SB):
                        sub.build(back_end, self.uuid, p)
                    elif isinstance(sub, odml2.Section):
                        # noinspection PyProtectedMember
                        sub._copy(back_end, self.uuid, p, True)
                    else:
                        ValueError("Section or SB expected, but type was '%s'" % type(sub))
            elif isinstance(thing, SB):
                thing.build(back_end, self.uuid, p)
            elif isinstance(thing, odml2.Section):
                # noinspection PyProtectedMember
                thing._copy(back_end, self.uuid, p, True)
            else:
                value = odml2.Value.from_obj(thing)
                back_end.sections[self.uuid].value_properties.set(p, value)
