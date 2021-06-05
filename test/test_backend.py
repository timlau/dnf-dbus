""" Unit Test for dnfdbus.backend """

import unittest
from unittest.mock import MagicMock, Mock, patch

import dnfdbus.client as client
from dnfdbus.backend import DnfBackend, DnfPkg, DnfRepository

TEST_PKGS = [
    "AtomicParsley-0.9.5-17.fc34.x86_64",
    "Box2D-2.4.1-5.fc34.x86_64",
    "Carla-1:2.3.0-1.fc34.x86_64",
    "Carla-vst-1:2.3.0-1.fc34.x86_64",
    "GraphicsMagick-1.3.36-3.fc34.x86_64",
    "ModemManager-1.16.4-1.fc34.x86_64",
    "ModemManager-glib-1.16.4-1.fc34.x86_64",
    "NetworkManager-1:1.30.4-1.fc34.x86_64",
    "NetworkManager-adsl-1:1.30.4-1.fc34.x86_64",
    "NetworkManager-bluetooth-1:1.30.4-1.fc34.x86_64",
]

TEST_PKG_LIST = [client.DnfPkg(pkg) for pkg in TEST_PKGS]

# define the allowed method of the Dnf Base Mock
DNF_MOCK_SPEC = [
    'read_all_repos',
    'fill_sack',
    'fill_sack_from_repos_in_cache',
    'sack'
]


def dnf_mock():
    """ Setup at dnf.Base Mock"""
    base = MagicMock(spec=DNF_MOCK_SPEC)
    repo1 = Mock()
    repo1.id = 'id1'
    repo1.name = 'id1'
    repo1.enabled = True
    repo2 = Mock()
    repo2.id = 'id2'
    repo2.name = 'id2'
    repo1.enabled = True
    repo3 = Mock()
    repo3.id = 'id3'
    repo3.name = 'id3'
    repo3.enabled = False
    base.repos = {"id1": repo1, "id2": repo2, "id3": repo3}
    return base


class TestRepository(unittest.TestCase):

    def setUp(self):
        self.mock = Mock(return_value=None)
        self.mock.id = "id"
        self.mock.enabled = True
        self.mock.name = "name"
        self.repo = DnfRepository(self.mock)

    def tearDown(self):
        pass

    def test_properties(self):
        repo_id = self.repo.id
        name = self.repo.name
        enabled = self.repo.enabled
        self.assertEqual(repo_id, 'id')
        self.assertEqual(name, 'name')
        self.assertEqual(enabled, True)


class TestDnfBackend(unittest.TestCase):

    def setUp(self):
        self.base = dnf_mock()
        self.backend = DnfBackend(self.base)

    def tearDown(self):
        pass

    def test_setup(self):
        """ Testing dnf setup is done only once"""
        self.assertEqual(self.backend.is_setup, False)
        res = self.backend.get_repositories()
        self.assertEqual(self.backend.is_setup, True)
        self.base.read_all_repos.assert_called()
        self.base.fill_sack_from_repos_in_cache.assert_called()
        res = self.backend.get_repositories()
        self.base.read_all_repos.assert_called_once()
        self.base.fill_sack_from_repos_in_cache.assert_called_once()

    def test_get_repositories(self):
        res = self.backend.get_repositories()
        self.assertIsInstance(res, list)
        self.assertEqual(len(res), 3)
        self.assertEqual(res[0].name, 'id1')
        self.assertEqual(res[1].name, 'id2')
        self.assertEqual(res[2].name, 'id3')
        self.assertEqual(res[2].enabled, False)


class TestDnfPackages(unittest.TestCase):

    def setUp(self):
        self.base = dnf_mock()
        self.backend = DnfBackend(self.base)

    def tearDown(self):
        pass

    def _assert_test_packages(self, pkgs: list):
        self.assertIsInstance(pkgs, list)
        self.assertEqual(len(pkgs), 10)
        pkg = pkgs[0]  # AtomicParsley-0.9.5-17.fc34.x86_64
        self.assertIsInstance(pkg, DnfPkg)
        self.assertEqual(pkg.name, 'AtomicParsley')
        self.assertEqual(pkg.version, '0.9.5')
        self.assertEqual(pkg.release, '17.fc34')
        self.assertEqual(pkg.arch, 'x86_64')
        self.assertEqual(pkg.epoch, '0')

    def test_pkg_installed(self):
        self.base.sack.query().installed.return_value = TEST_PKG_LIST
        pkgs = self.backend.packages
        res = pkgs.installed
        self._assert_test_packages(res)

    def test_pkg_available(self):
        self.base.sack.query().available().latest.return_value = TEST_PKG_LIST
        pkgs = self.backend.packages
        res = pkgs.available
        self._assert_test_packages(res)

    @patch('dnf.subject.Subject')
    def test_pkg_by_key(self, mock_sbj):
        mock_sbj().get_best_query.return_value = TEST_PKG_LIST
        pkgs = self.backend.packages
        res = pkgs.by_key("*qt6*")
        # dnf.subject.Subject method calls
        mock_sbj.assert_called_with('*qt6*')
        mock_sbj().get_best_query.assert_called()
        # returns list of DnfPkg
        self._assert_test_packages(res)

    def test_pkg_by_filter_installed(self):
        self.base.sack.query().installed.return_value = TEST_PKG_LIST
        pkgs = self.backend.packages
        res = pkgs.by_filter('installed')
        self._assert_test_packages(res)

    def test_pkg_by_filter_availabe(self):
        self.base.sack.query().available().latest.return_value = TEST_PKG_LIST
        pkgs = self.backend.packages
        res = pkgs.by_filter('available')
        self._assert_test_packages(res)

    def test_pkg_by_filter_updates(self):
        self.base.sack.query().upgrades().latest.return_value = TEST_PKG_LIST
        pkgs = self.backend.packages
        res = pkgs.by_filter('updates')
        self._assert_test_packages(res)

    def test_pkg_by_filter_notfound(self):
        pkgs = self.backend.packages
        inst = pkgs.by_filter('NOTFOUND')
        self.assertIsInstance(inst, list)
        self.assertEqual(len(inst), 0)
