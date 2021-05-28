import unittest
import re

from unittest.mock import MagicMock, Mock, patch

from dnfdbus.misc import to_nevra


class TestMisc(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_nevra(self):
        pkgs = ['foo-bar-7:2.3.0-1.fc34.x86_64',
                'foo-2.3.0-1.fc34.x86_64', 'foo-too-loo-3:2.3.0-1.fc34.noarch']
        n, e, v, r, a = to_nevra(pkgs[0])
        self.assertEqual(n, 'foo-bar')
        self.assertEqual(e, '7')
        self.assertEqual(v, '2.3.0')
        self.assertEqual(r, '1.fc34')
        self.assertEqual(a, 'x86_64')

        n, e, v, r, a = to_nevra(pkgs[1])
        self.assertEqual(n, 'foo')
        self.assertEqual(e, '0')
        self.assertEqual(v, '2.3.0')
        self.assertEqual(r, '1.fc34')
        self.assertEqual(a, 'x86_64')

        n, e, v, r, a = to_nevra(pkgs[2])
        self.assertEqual(n, 'foo-too-loo')
        self.assertEqual(e, '3')
        self.assertEqual(v, '2.3.0')
        self.assertEqual(r, '1.fc34')
        self.assertEqual(a, 'noarch')

        n, e, v, r, a = to_nevra(
            'qt6-qttools-libs-designercomponents-6.0.1-1.fc34.x86_64')
        self.assertEqual(n, 'qt6-qttools-libs-designercomponents')
        self.assertEqual(e, '0')
        self.assertEqual(v, '6.0.1')
        self.assertEqual(r, '1.fc34')
        self.assertEqual(a, 'x86_64')
