import unittest
import json

from unittest.mock import MagicMock, Mock, patch

from dnfdbus.client import DnfDbusClient, DnfRepo, DnfPkg


class TestClient(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testDnfPkg(self):
        pkg = DnfPkg('foo-too-loo-3:2.3.0-1.fc34.noarch' )
        self.assertEqual(pkg.name,'foo-too-loo')
        self.assertEqual(pkg.epoch,'3')
        self.assertEqual(pkg.version,'2.3.0')
        self.assertEqual(pkg.release,'1.fc34')
        self.assertEqual(pkg.arch,'noarch')

    def testDnfRepo(self):
        repo = DnfRepo({'id': "repo-id", "name": "repo name", 'enabled': True})
        self.assertEqual(repo.id, "repo-id")
        self.assertEqual(repo.name, "repo name")
        self.assertEqual(repo.enabled, True)

    def testDnfClient(self):
        client = DnfDbusClient()
        client.proxy = MagicMock()
        client.get_version()
        client.proxy.Version.assert_called
        client.quit()
        client.proxy.Quit.assert_called
        client.proxy.GetRepositories.return_value = json.dumps([{'id': "repo-id", "name": "repo name", 'enabled': True}])
        repos = client.get_repositories()
        self.assertIsInstance(repos, list)
        repo = repos[0]
        self.assertIsInstance(repo, DnfRepo)
        self.assertEqual(repo.id, "repo-id")
        self.assertEqual(repo.name, "repo name")
        self.assertEqual(repo.enabled, True)
        client.proxy.GetPackagesByKey.return_value = json.dumps(['foo-too-loo-3:2.3.0-1.fc34.noarch'])
        pkgs = client.get_packages_by_key("*too-loo*")
        self.assertIsInstance(pkgs, list)
        pkg = pkgs[0]
        self.assertIsInstance(pkg, DnfPkg)
        self.assertEqual(pkg.name,'foo-too-loo')
        self.assertEqual(pkg.epoch,'3')
        self.assertEqual(pkg.version,'2.3.0')
        self.assertEqual(pkg.release,'1.fc34')
        self.assertEqual(pkg.arch,'noarch')





