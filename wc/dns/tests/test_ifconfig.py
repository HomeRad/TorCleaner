# -*- coding: iso-8859-1 -*-
# Copyright (C) 2005-2006 Bastian Kleineidam
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

import unittest


class TestIfconfig (unittest.TestCase):

    needed_resources = ['posix']

    def test_interfaces (self):
        import wc.dns.ifconfig
        ifconf = wc.dns.ifconfig.IfConfig()
        iflist = ifconf.getInterfaceList()
        for interface in iflist:
            flags = ifconf.getFlags(interface)
            addr = ifconf.getAddr(interface)
            mask = ifconf.getMask(interface)
            broadcast = ifconf.getBroadcast(interface)
            is_up = ifconf.isUp(interface)
            is_loopback = ifconf.isLoopback(interface)


def test_suite ():
    return unittest.makeSuite(TestIfconfig)


if __name__ == '__main__':
    unittest.main()
