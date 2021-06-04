import json
import unittest
from unittest.mock import MagicMock

from dnfdbus.client import DnfDbusClient, DnfPkg, DnfRepo


class TestDnfPkg(unittest.TestCase):

    def testDnfPkg(self):
        pkg = DnfPkg('foo-too-loo-3:2.3.0-1.fc34.noarch')
        self.assertEqual(pkg.name, 'foo-too-loo')
        self.assertEqual(pkg.epoch, '3')
        self.assertEqual(pkg.version, '2.3.0')
        self.assertEqual(pkg.release, '1.fc34')
        self.assertEqual(pkg.arch, 'noarch')


class TestDnfRepo(unittest.TestCase):

    def testDnfRepo(self):
        repo = DnfRepo({'id': "repo-id", "name": "repo name", 'enabled': True})
        self.assertEqual(repo.id, "repo-id")
        self.assertEqual(repo.name, "repo name")
        self.assertEqual(repo.enabled, True)


class TestClient(unittest.TestCase):

    def setUp(self):
        self.client = DnfDbusClient()
        self.client.proxy = MagicMock()

    def testVersion(self):
        """ Test version property """
        self.client.proxy.Version = '7.0'
        ver = self.client.version
        self.assertEqual(ver, '7.0')

    def testQuit(self):
        """ Test quit() method"""

        self.client.quit()
        self.client.proxy.Quit.assert_called()

    def testGetRepoitories(self):
        """ Test get_repositories() method """
        self.client.proxy.GetRepositories.return_value = json.dumps(
            [{'id': "repo-id", "name": "repo name", 'enabled': True}])
        repos = self.client.get_repositories()
        self.assertIsInstance(repos, list)
        repo = repos[0]
        self.assertIsInstance(repo, DnfRepo)
        self.assertEqual(repo.id, "repo-id")
        self.assertEqual(repo.name, "repo name")

    def check_async_called(self, name, *args):
        # Check the expected parameters of the DnfDbusClient.async_dbus.call(arg0, arg1, .., argN)
        mock = self.client.async_dbus.call.call_args[0][0]  # first parameters
        params = self.client.async_dbus.call.call_args[0][1:]  # the rest of the parameters
        self.assertEqual(mock._mock_name, name)
        ndx = 0
        for arg in args:
            self.assertEqual(arg, params[ndx])
            ndx += 1

    def testGetPackagesByKey(self):
        """ Test get_packages_by_key() method"""
        self.client.async_dbus = MagicMock()
        self.client.async_dbus.call.return_value = json.dumps(
            ['foo-too-loo-3:2.3.0-1.fc34.noarch'])
        pkgs = self.client.get_packages_by_key("*too-loo*")
        self.check_async_called('GetPackagesByKey', "*too-loo*")
        self.assertIsInstance(pkgs, list)
        pkg = pkgs[0]
        self.assertIsInstance(pkg, DnfPkg)
        self.assertEqual(pkg.name, 'foo-too-loo')
        self.assertEqual(pkg.epoch, '3')
        self.assertEqual(pkg.version, '2.3.0')
        self.assertEqual(pkg.release, '1.fc34')
        self.assertEqual(pkg.arch, 'noarch')
