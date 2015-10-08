# coding=UTF-8

# Copyright (c) 2015, Adrian Stoewer (adrian.stoewer@rz.ifi.lmu.de)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the project.

import io
import unittest
import datetime as dt
from uuid import uuid4

from odml2 import Document, SB, Value
from odml2.back_end.yaml_io import YamlBackEnd


class YamlBackEndTest(unittest.TestCase):

    def setUp(self):
        self.empty = YamlBackEnd()

    def test_autosave(self):
        self.assertFalse(self.empty.autosave)

    def test_root(self):
        be = self.empty
        self.assertFalse(be.root_exists())
        be.root_create("Experiment", label="Experiment 01", reference="./example.dat")
        self.assertTrue(be.root_exists())
        root_id = be.root_get()
        self.assertTrue(be.section_exists(root_id))
        self.assertEqual(be.section_get_type(root_id), "Experiment")
        self.assertEqual(be.section_get_label(root_id), "Experiment 01")
        self.assertEqual(be.section_get_reference(root_id), "./example.dat")
        be.section_remove(root_id)
        self.assertFalse(be.section_exists(root_id))
        self.assertFalse(be.root_exists())

    def test_value(self):
        be = self.empty
        be.root_create("Experiment", label="Experiment 01", reference="./example.dat")
        root_id = be.root_get()
        be.property_set_value(root_id, "date", Value("2011-10-31"))
        self.assertListEqual(be.section_get_properties(root_id), ["date"])
        be.property_remove_value(root_id, "date")
        self.assertListEqual(be.section_get_properties(root_id), [])

    def test_subsections(self):
        ids = tuple(str(uuid4()) for _ in range(4))
        id_1, id_11, id_111, id_112 = ids
        be = self.empty
        be.root_create("type", id_1, "root")
        be.property_add_section(id_1, "prop_11", "type", id_11)
        be.property_add_section(id_11, "prop_111", "type", id_111)
        be.property_add_section(id_11, "prop_112", "type", id_112)
        for i in ids:
            self.assertTrue(be.section_exists(i))
        self.assertListEqual(be.section_get_properties(id_1), ["prop_11"])
        self.assertListEqual(be.section_get_properties(id_11), ["prop_111", "prop_112"])

        be.section_remove(id_11)
        self.assertTrue(be.section_exists(id_1))
        for i in ids[1:]:
            self.assertFalse(be.section_exists(i))

    def test_marshalling(self):
        be = YamlBackEnd()
        doc = Document("./example.yaml", be)
        doc.author = "John Doe"
        doc.date = dt.date.today()
        doc.root = SB(
            typ="RecordingSession",
            label="session one",
            date=dt.date.today(),
            experimenter=SB(
                typ="Person",
                first_name="John",
                last_name="Doe",
                birthday=dt.date(1970, 11, 11)
            ),
            stimuli=[
                SB(
                    typ="PulseStimulus",
                    label="first pulse",
                    offset="10ms",
                    duration=Value(5, "ms"),
                    current="0.6nA+-0.001"
                ),
                SB(
                    typ="PulseStimulus",
                    label="second pulse",
                    offset="30ms",
                    duration="5ms",
                    current=Value(0.8, "nA", 0.001)
                )
            ]
        )
        with io.StringIO() as str_io:
            be.save(str_io)
            yaml_str = str_io.getvalue()
        with io.StringIO(yaml_str) as str_io:
            be = YamlBackEnd()
            be.load(str_io)
        with io.StringIO() as str_io:
            be.save(str_io)
            other_yaml_str = str_io.getvalue()
        self.assertEqual(yaml_str, other_yaml_str)
