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

import winreg


def get_localaddrs ():
    """all active interfaces' ip addresses"""
    try: # search interfaces
        key = winreg.key_handle(winreg.HKEY_LOCAL_MACHINE,
           r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces")
        for subkey in key.subkeys():
            pass # XXX todo
    except EnvironmentError:
        pass
    return []


def resolver_config (config):
    """get DNS config from Windows registry settings"""
    key = None
    try:
        key = winreg.key_handle(winreg.HKEY_LOCAL_MACHINE,
               r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters")
    except EnvironmentError:
        try: # for Windows ME
            key = winreg.key_handle(winreg.HKEY_LOCAL_MACHINE,
                    r"SYSTEM\CurrentControlSet\Services\VxD\MSTCP")
        except EnvironmentError:
            pass
    if key:
        for server in winreg.stringdisplay(key.get("NameServer", "")):
            if server:
                config.nameservers.append(str(server))
        for item in winreg.stringdisplay(key.get("SearchList", "")):
            if item:
                config.search_domains.append(str(item))
        if not config.nameservers:
            # XXX the proper way to test this is to search for
            # the "EnableDhcp" key in the interface adapters...
            for server in winreg.stringdisplay(key.get("DhcpNameServer", "")):
                if server:
                    config.nameservers.append(str(server))
            for item in winreg.stringdisplay(key.get("DhcpDomain", "")):
                if item:
                    config.search_domains.append(str(item))

    try: # search adapters
        key = winreg.key_handle(winreg.HKEY_LOCAL_MACHINE,
  r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\DNSRegisteredAdapters")
        for subkey in key.subkeys():
            values = subkey.get('DNSServerAddresses', "")
            for server in winreg.binipdisplay(values):
                if server:
                    config.nameservers.append(server)
    except EnvironmentError:
        pass

    try: # search interfaces
        key = winreg.key_handle(winreg.HKEY_LOCAL_MACHINE,
           r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces")
        for subkey in key.subkeys():
            for server in winreg.stringdisplay(subkey.get('NameServer', '')):
                if server:
                    config.nameservers.append(server)
    except EnvironmentError:
        pass


