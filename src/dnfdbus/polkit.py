#    Copyright (C) 2021 Tim Lauridsen < tla[at]rasmil.dk >
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to
#    the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA


""" Module for PolicyKit Authentication 

Use Legacy python dbus, because dasbus don’t work with PolicyKit1

"""

import dbus

bus = dbus.SystemBus()
DBUS_SENDER = bus.get_unique_name()


def check_permission(action):
    proxy = bus.get_object('org.freedesktop.PolicyKit1',
                           '/org/freedesktop/PolicyKit1/Authority')
    authority = dbus.Interface(
        proxy, dbus_interface='org.freedesktop.PolicyKit1.Authority')
    subject = ('system-bus-name', {'name': DBUS_SENDER})
    action_id = action
    details = {}
    flags = 1            # AllowUserInteraction flag
    cancellation_id = ''  # No cancellation id

    (granted, _, details) = authority.CheckAuthorization(
        subject, action_id, details, flags, cancellation_id)

    return granted == dbus.Boolean(True)


if __name__ == "__main__":
    print(f'Sender : {DBUS_SENDER}')
    granted = check_permission('dk.rasmil.DnfDbus.read')
    print(granted)
