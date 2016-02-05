# coding=UTF-8

# Copyright (c) 2015, Adrian Stoewer (adrian.stoewer@rz.ifi.lmu.de)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the project.

"""
Provides a back-and implementation for yaml using the memory back-end base classes.
"""

import io
import six
import yaml
from collections import OrderedDict

from odml2.api import mem


class YamlDocument(mem.MemDocument):

    NAME = "yaml"
    FEXT = ("yml", "yaml")
    MIME = ("text/yaml", "text/x-yaml", "application/yaml", "application/x-yaml")

    def __init__(self, is_writable=True):
        super(YamlDocument, self).__init__(is_writable)

    def close(self):
        raise NotImplementedError()

    def save(self, source):
        data = self.to_dict()
        if hasattr(source, "write"):
            yaml_str = yaml.dump(data, default_flow_style=False, allow_unicode=True)
            if six.PY2:
                yaml_str = yaml_str.decode("utf-8")
            source.write(yaml_str)
            if hasattr(source, "name"):
                self.set_uri(source.name)
        else:
            with io.open(source, "w", encoding="utf-8") as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
                self.set_uri(source)

    def load(self, dest):
        if hasattr(dest, "read"):
            data = yaml.load(dest)
            if hasattr(dest, "name"):
                self.set_uri(dest.name)
        else:
            with io.open(dest, "r", encoding="utf-8") as f:
                data = yaml.load(f)
                self.set_uri(dest)
        self.from_dict(data)


def __ordered_dict_representer(dumper, ordered_dict):
    nodes = [(dumper.represent_data(k), dumper.represent_data(v)) for k, v in ordered_dict.items()]
    return yaml.nodes.MappingNode(u'tag:yaml.org,2002:map', nodes)

yaml.add_representer(OrderedDict, __ordered_dict_representer)
