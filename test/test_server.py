import unittest
from unittest.mock import MagicMock, patch
from dnfdbus.server import DnfDbus


class TestDnfDbus (unittest.TestCase):

    def setUp(self):
        loop = MagicMock()
        self.dbus = DnfDbus(loop)
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
