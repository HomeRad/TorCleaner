# -*- coding: iso-8859-1 -*-
"""network utilities for windows platforms"""
# Copyright (C) 2004  Bastian Kleineidam
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

__version__ = "$Revision$"[11:-2]
__date__    = "$Date$"[7:-2]

import sets
import wc.winreg


def get_localaddrs ():
    """all active interfaces' ip addresses"""
    addrs = sets.Set()
    try: # search interfaces
        key = wc.winreg.key_handle(wc.winreg.HKEY_LOCAL_MACHINE,
           r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces")
        for subkey in key.subkeys():
            if subkey.get('EnableDHCP')==1:
                ip = subkey.get('DhcpIPAddress')
            else:
                ip = subkey.get('IPAddress')
            if ip:
                addrs.add(ip)
    except EnvironmentError:
        pass
    return addrs


def resolver_config (config):
    """get DNS config from Windows registry settings"""
    try:
        key = wc.winreg.key_handle(wc.winreg.HKEY_LOCAL_MACHINE,
               r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters")
    except EnvironmentError:
        try: # for Windows ME
            key = wc.winreg.key_handle(wc.winreg.HKEY_LOCAL_MACHINE,
                    r"SYSTEM\CurrentControlSet\Services\VxD\MSTCP")
        except EnvironmentError:
            key = None
    if key:
        if key.get('EnableDHCP')==1:
            servers = wc.winreg.stringdisplay(key.get("DhcpNameServer", ""))
            domains = wc.winreg.stringdisplay(key.get("DhcpDomain", ""))
        else:
            servers = wc.winreg.stringdisplay(key.get("NameServer", ""))
            domains = wc.winreg.stringdisplay(key.get("SearchList", ""))
        print "XXX1a", servers
        print "XXX1b", domains
        config.nameservers.extend([ str(s) for s in servers if s ])
        config.domains.extend([ str(d) for d in domains if d ])
    try: # search adapters
        key = wc.winreg.key_handle(wc.winreg.HKEY_LOCAL_MACHINE,
  r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\DNSRegisteredAdapters")
    except EnvironmentError:
        key = None
    if key:
        for subkey in key.subkeys():
            values = subkey.get("DNSServerAddresses", "")
            servers = wc.winreg.binipdisplay(values)
            print "XXX2", servers
            config.nameservers.extend([ str(s) for s in servers if s ])
    try: # search interfaces
        key = wc.winreg.key_handle(wc.winreg.HKEY_LOCAL_MACHINE,
           r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces")
    except EnvironmentError:
        key = None
    if key:
        for subkey in key.subkeys():
            if subkey.get('EnableDHCP')==1:
                servers = wc.winreg.stringdisplay(subkey.get('DhcpNameServer', ''))
            else:
                servers = wc.winreg.stringdisplay(subkey.get('NameServer', ''))
            print "XXX3", servers
            config.nameservers.extend([ str(s) for s in servers if s ])

