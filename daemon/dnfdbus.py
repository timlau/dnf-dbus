#!/usr/bin/python3
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.

# (C) 2021 Tim Lauridsen <tla<at>rasmil.dk>

#
# dnf dBus service

# FIXME: Hack for gobject don't blow up'
import os
os.environ['XDG_RUNTIME_DIR'] = '/root'

from dasbus.loop import EventLoop
from dasbus.connection import SystemMessageBus

from dnfdbus.dbus import DnfDbus

loop = EventLoop()
bus = SystemMessageBus()
bus.publish_object("/dk/rasmil/DnfDbus", DnfDbus(loop))
bus.register_service("dk.rasmil.DnfDbus")
loop.run()
