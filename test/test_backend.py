""" Unit Test for dnfdbus.backend """

import unittest
import re
from unittest.mock import MagicMock, Mock, patch

from dnf import query, subject
import dnfdbus.backend as backend


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

NEVRA_RE = re.compile(r'([a-z\-]*?)(-([0-9]*):|-)([0-9\.]*)-([0-9a-z\.]*)\.([a-z0-9_]*)$',re.IGNORECASE)


def to_nerva(pkg):
    match = NEVRA_RE.search(pkg)
    n = match.group(1)
    if match.group(3):
        e = match.group(3)
    else:
        e = '0'
    v = match.group(4)
    r = match.group(5)
    a = match.group(6)
    #print(f'{n=} {e=} {v=} {r=} {a=}')
    return n,e,v,r,a

class TestPkg:
    def __init__(self, pkg) -> None:
        self.n,self.e,self.v,self.r,self.a = to_nerva(pkg)

    def __repr__(self) -> str:
        if self.e == '0':
            return f'{self.n}-{self.v}-{self.r}.{self.a}'
        else:
            return f'{self.n}-{self.e}:{self.v}-{self.r}.{self.a}'


    @property
    def name(self):
        return self.n

    @property
    def version(self):
        return self.v

    @property
    def release(self):
        return self.r

    @property
    def arch(self):
        return self.a

    @property
    def epoch(self):
        return self.e

TEST_PKG_LIST = [TestPkg(pkg) for pkg in TEST_PKGS]        



# define the allowed method of the Dnf Base Mock
DNF_MOCK_SPEC = [
    'read_all_repos',
    'fill_sack',
    'fill_sack_from_repos_in_cache',
    'sack'
]

def build_pkgs():
    for pkg in TEST_PKGS:
        to_nerva(pkg)

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
        self.repo = backend.DnfRepository(self.mock)

    def tearDown(self):
        pass

    def test_properties(self):
        id = self.repo.id
        name = self.repo.name
        enabled = self.repo.enabled
        self.assertEqual(id, 'id')
        self.assertEqual(name, 'name')
        self.assertEqual(enabled, True)





class TestDnfBackend(unittest.TestCase):

    def setUp(self):
        self.base = dnf_mock()
        self.backend = backend.DnfBackend(self.base)

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

    def test_pkg_installed(self):
        self.base.sack.query().installed.return_value = TEST_PKG_LIST
        pkgs = self.backend.packages
        inst = pkgs.installed
        self.assertIsInstance(inst, list)
        self.assertEqual(len(inst), 10)
        pkg = inst[0] # AtomicParsley-0.9.5-17.fc34.x86_64
        self.assertIsInstance(pkg, backend.DnfPkg)
        self.assertEqual(pkg.name,'AtomicParsley')
        self.assertEqual(pkg.version,'0.9.5')
        self.assertEqual(pkg.release,'17.fc34')
        self.assertEqual(pkg.arch,'x86_64')
        self.assertEqual(pkg.epoch,'0')

    def test_pkg_available(self):
        self.base.sack.query().available().latest.return_value = TEST_PKG_LIST
        pkgs = self.backend.packages
        inst = pkgs.available
        #print(f'{inst=}')
        self.assertIsInstance(inst, list)
        self.assertEqual(len(inst), 10)
        pkg = inst[0] # AtomicParsley-0.9.5-17.fc34.x86_64
        self.assertIsInstance(pkg, backend.DnfPkg)
        self.assertEqual(pkg.name,'AtomicParsley')
        self.assertEqual(pkg.version,'0.9.5')
        self.assertEqual(pkg.release,'17.fc34')
        self.assertEqual(pkg.arch,'x86_64')
        self.assertEqual(pkg.epoch,'0')
    
    @patch('dnf.subject.Subject')
    def test_pkg_by_key(self, mock_sbj):
        mock_sbj().get_best_query.return_value = TEST_PKG_LIST
        pkgs = self.backend.packages
        res = pkgs.by_key("*qt6*") 
        # dnf.subject.Subject method calls
        mock_sbj.assert_called_with('*qt6*')
        mock_sbj().get_best_query.assert_called()
        # returns list of DnfPkg
        self.assertIsInstance(res, list)
        self.assertIsInstance(res[0], backend.DnfPkg)

if __name__ == '__main__':
    #unittest.main()
    build_pkgs()
