import unittest
from collections import namedtuple
from unittest.mock import MagicMock, Mock, patch
from dnfdbus.backend.groups import DnfGrpPackage, DnfGroup, DnfCategory, DnfComps

FakePO = namedtuple('Package', 'name option_type')
PO_LIST = [DnfGrpPackage(FakePO("foo", 4)), DnfGrpPackage(FakePO("bar", 3))]


class Fake:

    def __init__(self, id, name, ui_name, ui_description):
        self.id = id
        self.name = name
        self.ui_name = ui_name
        self.ui_description = ui_description


class FakeGroup(Fake):
    def packages_iter(self):
        return PO_LIST


GRP_LIST = [DnfGroup(None, FakeGroup("grp_id", "grp_name",
                                     "grp_ui_name", "grp_ui_description"))]


class FakeCategory(Fake):
    def groups_iter(self):
        return GRP_LIST


FAKE_CAT = [FakeCategory("cat_id", "cat_name",
                         "cat_ui_name", "cat_ui_description")]


class FakeComps:
    def categories_iter(self):
        return FAKE_CAT


class TestDnfGrpPackage(unittest.TestCase):

    def setUp(self):
        self.pkg = DnfGrpPackage(FakePO("Foobar", 4))

    def test_package(self):
        self.assertEqual(self.pkg.name, "Foobar")
        self.assertEqual(self.pkg.option_type, 4)

    def test_str_repr(self):
        self.assertEqual(str(self.pkg), "Foobar")
        self.assertEqual(repr(self.pkg), "DnfGrpPackage(Foobar)")


class TestDnfGroup(unittest.TestCase):

    def setUp(self):
        fake_grp = FakeGroup("id", "name", "ui_name", "ui_description")
        cat = None
        self.grp = DnfGroup(cat, fake_grp)

    def test_properties(self):
        self.assertEqual(self.grp.id, "id")
        self.assertEqual(self.grp.name, "name")
        self.assertEqual(self.grp.ui_name, "ui_name")
        self.assertEqual(self.grp.ui_description, "ui_description")

    def test_str_repr(self):
        self.assertEqual(str(self.grp), "name")
        self.assertEqual(repr(self.grp), "DnfGroup(id, name)")

    def test_packages(self):
        pkgs = self.grp.packages
        self.assertIsInstance(pkgs, list)
        self.assertEqual(len(pkgs), 2)
        po = pkgs[0]
        self.assertIsInstance(po, DnfGrpPackage)

    def test_load(self):
        self.grp._load = MagicMock()
        pkgs = self.grp.packages
        self.grp._load.assert_called_once()
        self.grp._packages = PO_LIST
        pkgs = self.grp.packages
        self.grp._load.assert_called_once()
        self.assertEqual(len(pkgs), 2)


class TestDnfCategory(unittest.TestCase):

    def setUp(self):
        self.cat = DnfCategory(FakeCategory(
            "cat_id", "cat_name", "cat_ui_name", "cat_ui_description"))

    def test_str_repr(self):
        self.assertEqual(str(self.cat), "cat_name")
        self.assertEqual(repr(self.cat), "DnfCategory(cat_id, cat_name)")

    def test_properties(self):
        self.assertEqual(self.cat.id, "cat_id")
        self.assertEqual(self.cat.name, "cat_name")
        self.assertEqual(self.cat.ui_name, "cat_ui_name")
        self.assertEqual(self.cat.ui_description, "cat_ui_description")

    def test_groups(self):
        grps = self.cat.groups
        self.assertIsInstance(grps, list)
        self.assertEqual(len(grps), 1)
        grp = grps[0]
        self.assertIsInstance(grp, DnfGroup)
        self.assertEqual(grp.id, "grp_id")

    def test_load(self):
        self.cat._load = MagicMock()
        grps = self.cat.groups
        self.cat._load.assert_called_once()
        grp = GRP_LIST[0]
        self.cat._groups = {grp.id: grp}
        grps = self.cat.groups
        self.cat._load.assert_called_once()
        self.assertEqual(len(grps), 1)


class TestComps(unittest.TestCase):

    def setUp(self):
        self.backend = MagicMock()
        self.backend.base = MagicMock()
        self.backend.base.comps = FakeComps()
        self.comps = DnfComps(self.backend)

    def test_setup(self):
        self.backend.setup.assert_called()
        self.backend.base.read_comps.assert_called()
        self.assertEqual(None, None)

    def test_categories(self):
        cats = self.comps.categories
        self.assertIsInstance(cats, list)
        self.assertEqual(len(cats), 1)
        cat = cats[0]
        self.assertIsInstance(cat, DnfCategory)
        self.assertEqual(cat.name, "cat_name")

    def test_groups(self):
        grps = self.comps.groups
        self.assertIsInstance(grps, list)
        self.assertEqual(len(grps), 1)
        grp = grps[0]
        self.assertIsInstance(grp, DnfGroup)
        self.assertEqual(grp.name, "grp_name")

    def test_load(self):
        self.comps._load = MagicMock()
        grps = self.comps.groups
        self.comps._load.assert_called_once()
        grp = GRP_LIST[0]
        self.comps._groups = {grp.id: grp}
        grps = self.comps.groups
        self.comps._load.assert_called_once()
        self.assertEqual(len(grps), 1)

    def test_dump_categories(self):
        res = self.comps.dump_categories()
        self.assertIsInstance(res, list)
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0], ['cat_id', 'cat_name',
                                  'cat_ui_name', 'cat_ui_description'])

    def test_dump_groups_by_category(self):
        res = self.comps.dump_groups_by_category('cat_id')
        print(self.comps._groups.keys())
        self.assertIsInstance(res, list)
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0], ['grp_id', 'grp_name',
                                  'grp_ui_name', 'grp_ui_description'])
