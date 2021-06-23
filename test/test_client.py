import json
import unittest
from unittest.mock import MagicMock

from dnfdbus.client import DnfDbusClient, Package, Repository


class TestPackage(unittest.TestCase):

    def testPackage(self):
        pkg = Package('foo-too-loo-3:2.3.0-1.fc34.noarch', 'myrepo')
        self.assertEqual(pkg.name, 'foo-too-loo')
        self.assertEqual(pkg.epoch, '3')
        self.assertEqual(pkg.version, '2.3.0')
        self.assertEqual(pkg.release, '1.fc34')
        self.assertEqual(pkg.arch, 'noarch')
        self.assertEqual(pkg.reponame, 'myrepo')
        self.assertEqual(str(pkg), 'foo-too-loo-3:2.3.0-1.fc34.noarch')
        self.assertEqual(
            repr(pkg), 'Package(foo-too-loo-3:2.3.0-1.fc34.noarch)')


class TestRepository(unittest.TestCase):

    def testRepository(self):
        repo = Repository(
            {'id': "repo-id", "name": "repo name", 'enabled': True})
        self.assertEqual(repo.id, "repo-id")
        self.assertEqual(repo.name, "repo name")
        self.assertEqual(repo.enabled, True)


class TestClient(unittest.TestCase):

    def setUp(self):
        self.client = DnfDbusClient()
        self.client.proxy = MagicMock()
        self.mock_async = MagicMock()
        self.mock_async_method = MagicMock()
        self.client.get_async_method = self.mock_async
        self.mock_async.return_value = self.mock_async_method

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
        self.mock_async_method.return_value = [
            {'id': "repo-id", "name": "repo name", 'enabled': True}]
        repos = self.client.get_repositories()
        self.mock_async.assert_called_with('GetRepositories')
        self.assertIsInstance(repos, list)
        repo = repos[0]
        self.assertIsInstance(repo, Repository)
        self.assertEqual(repo.id, "repo-id")
        self.assertEqual(repo.name, "repo name")

    def testGetPackagesByKey(self):
        """ Test get_packages_by_key() method"""
        self.mock_async_method.return_value = [
            ['foo-too-loo-3:2.3.0-1.fc34.noarch', 'myrepo']]
        pkgs = self.client.get_packages_by_key("*too-loo*")
        self.mock_async.assert_called_with("GetPackagesByKey")
        self.mock_async_method.assert_called_with("*too-loo*")
        self.assertIsInstance(pkgs, list)
        pkg = pkgs[0]
        self.assertIsInstance(pkg, Package)
        self.assertEqual(pkg.name, 'foo-too-loo')
        self.assertEqual(pkg.epoch, '3')
        self.assertEqual(pkg.version, '2.3.0')
        self.assertEqual(pkg.release, '1.fc34')
        self.assertEqual(pkg.arch, 'noarch')
        self.assertEqual(pkg.reponame, 'myrepo')

    def testGetPackagesByFilter(self):
        """ Test get_packages_by_filter() method"""
        self.mock_async_method.return_value = [
            ['foo-too-loo-3:2.3.0-1.fc34.noarch', 'myrepo']]
        pkgs = self.client.get_packages_by_filter("installed", False)
        self.mock_async.assert_called_with("GetPackagesByFilter")
        self.mock_async_method.assert_called_with("installed", False)
        self.assertIsInstance(pkgs, list)
        pkg = pkgs[0]
        self.assertIsInstance(pkg, Package)
        self.assertEqual(pkg.name, 'foo-too-loo')
        self.assertEqual(pkg.epoch, '3')
        self.assertEqual(pkg.version, '2.3.0')
        self.assertEqual(pkg.release, '1.fc34')
        self.assertEqual(pkg.arch, 'noarch')
        self.assertEqual(pkg.reponame, 'myrepo')

    def testGetPackagesByFilterExtra(self):
        """ Test get_packages_by_key() method"""
        self.mock_async_method.return_value = [
            ['foo-too-loo-3:2.3.0-1.fc34.noarch', 'myrepo', 'package summary', 100000]]
        pkgs = self.client.get_packages_by_filter("installed", True)
        self.mock_async.assert_called_with("GetPackagesByFilter")
        self.mock_async_method.assert_called_with("installed", True)
        self.assertIsInstance(pkgs, list)
        pkg = pkgs[0]
        self.assertIsInstance(pkg, Package)
        self.assertEqual(pkg.name, 'foo-too-loo')
        self.assertEqual(pkg.epoch, '3')
        self.assertEqual(pkg.version, '2.3.0')
        self.assertEqual(pkg.release, '1.fc34')
        self.assertEqual(pkg.arch, 'noarch')
        self.assertEqual(pkg.reponame, 'myrepo')
        self.assertEqual(pkg.size, 100000)
        self.assertEqual(pkg.summary, 'package summary')

    def testGetPackageAttribute(self):
        """ Test get_package_attribues() method"""
        self.mock_async_method.return_value = [('qt6-assistant-6.1.0-2.fc34.x86_64', '@System', 'Documentation browser for Qt6.'),
                                               ('qt6-assistant-6.1.0-2.fc34.x86_64', 'updates', 'Documentation browser for Qt6.')]
        res = self.client.get_package_attribute(
            "qt6-assistant-6.1.0-2.fc34.x86_64", "", "description")
        self.mock_async.assert_called_with("GetPackageAttribute")
        self.mock_async_method.assert_called_with(
            "qt6-assistant-6.1.0-2.fc34.x86_64", "", "description")
        self.assertIsInstance(res, list)
        self.assertEqual(2, len(res))
        elem = res[0]
        nevra, reponame, desc = elem
        self.assertEqual(nevra, 'qt6-assistant-6.1.0-2.fc34.x86_64')
        self.assertEqual(reponame, '@System')
        self.assertEqual(desc, 'Documentation browser for Qt6.')

    def test_GetCategories(self):
        self.mock_async_method.return_value = ["Category"]
        res = self.client.get_categories()
        self.mock_async.assert_called_with("GetCategories")
        self.assertEqual(res, ['Category'])
