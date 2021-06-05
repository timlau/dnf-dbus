import unittest
from dataclasses import dataclass
from unittest.mock import MagicMock, patch
from dnfdbus.server import DnfDbus, AccessDeniedError
from dnfdbus.backend import DnfPkg, DnfRepository


@dataclass
class FakePkg:
    """ Fake dnf package"""
    name: str = 'foo-too-loo'
    epoch: str = '3'
    version: str = '2.3.0'
    release: str = '1.fc34'
    arch: str = 'noarch'
    reponame: str = 'myrepo'

    def __str__(self):
        if self.epoch == '0':
            return f'{self.name}-{self.version}-{self.release}.{self.arch}'
        else:
            return f'{self.name}-{self.epoch}:{self.version}-{self.release}.{self.arch}'


class FakeRepo:
    def __init__(self, repo_id, name, enabled):
        self.id = repo_id
        self.name = name
        self.enabled = enabled


class TestDnfDbus (unittest.TestCase):

    def setUp(self):
        self.mock_loop = MagicMock()
        self.dbus = DnfDbus(self.mock_loop)
        self.dbus.backend = MagicMock()
        self.perm_mock = MagicMock(return_value=True)

    def tearDown(self):
        pass

    def _overload_permission(self):
        """ Overload the methods used to check for PolicyKit Access """
        self.dbus.check_permission_read = self.perm_mock
        self.dbus.check_permission_write = self.perm_mock

    @patch('dnfdbus.server.check_permission')
    @patch('dnfdbus.server.DBUS_SENDER')
    def test_permission_checks(self, mock_sender, mock_cp):
        mock_cp.return_value = True
        self.dbus.working_start()
        mock_cp.assert_called_with('dk.rasmil.DnfDbus.write')
        self.assertIn(mock_sender, self.dbus.authorized_sender_write)
        self.assertEqual(self.dbus._is_working, True)
        self.dbus.working_start(write=False)
        mock_cp.assert_called_with('dk.rasmil.DnfDbus.read')
        self.assertIn(mock_sender, self.dbus.authorized_sender_read)
        self.assertEqual(self.dbus._is_working, True)

    @patch('dnfdbus.server.check_permission')
    @patch('dnfdbus.server.DBUS_SENDER')
    def test_permission_fail(self, mock_sender, mock_cp):
        """ test AccessDeniedError exception if permission is not granted """
        mock_cp.return_value = False
        with self.assertRaises(AccessDeniedError):
            self.dbus.working_start()
        mock_cp.assert_called_with('dk.rasmil.DnfDbus.write')

    def test_working_start(self):
        self._overload_permission()
        self.dbus.working_start()
        self.assertEqual(self.dbus._is_working, True)
        self.dbus.working_start(write=False)
        self.assertEqual(self.dbus._is_working, True)

    def test_working_end(self):
        res = self.dbus.working_ended('foobar')
        self.assertEqual(self.dbus._is_working, False)
        self.assertEqual(res, 'foobar')

    def test_version(self):
        res = self.dbus.version()
        self.assertEqual(res, 'Version : 1.0')

    def test_quit(self):
        self._overload_permission()
        self.dbus._signal_quitting = MagicMock()
        self.dbus.quit()
        self.dbus._signal_quitting.emit.assert_called()
        self.mock_loop.quit.assert_called()

    def test_get_repositories(self):
        self._overload_permission()
        self.dbus.backend.get_repositories.return_value = [DnfRepository(FakeRepo('repoid', 'reponame', True))]
        res = self.dbus.get_repositories()
        self.assertIsInstance(res, str)
        self.assertEqual(res, '[{"id": "repoid", "name": "reponame", "enabled": true}]')

    def test_get_packages_by_key(self):
        self._overload_permission()
        pkgs_mock = MagicMock()
        self.dbus.backend.packages = pkgs_mock
        pkgs_mock.by_key.return_value = [DnfPkg(FakePkg())]
        res = self.dbus.get_packages_by_key("foobar")
        self.assertIsInstance(res, str)
        self.assertEqual(res, '["foo-too-loo-3:2.3.0-1.fc34.noarch;myrepo"]')

    def test_get_packages_by_filter(self):
        self._overload_permission()
        pkgs_mock = MagicMock()
        self.dbus.backend.packages = pkgs_mock
        pkgs_mock.by_filter.return_value = [DnfPkg(FakePkg())]
        res = self.dbus.get_packages_by_filter("installed")
        self.assertIsInstance(res, str)
        self.assertEqual(res, '["foo-too-loo-3:2.3.0-1.fc34.noarch;myrepo"]')
