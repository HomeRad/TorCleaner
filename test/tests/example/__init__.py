# -*- coding: iso-8859-1 -*-
"""example test"""
# Copyright (C) 2003-2004  Bastian Kleineidam
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

# sample client send file
client_send = """GET http://localhost:%(port)d/ HTTP/1.0\r
Host: localhost\r
X-Calvin: Wheeeeeee!\r
\r
This is POST data
"""
# sample server receive file
server_recv = """GET http://localhost:%(port)d/ HTTP/1.0\r
Host: localhost\r
X-Calvin: Wheeeeeee!\r
\r
This is POST data
"""
# sample server send file
server_send = """HTTP/1.0 200 Okidoki\r
Host: localhost\r
X-Hobbes: Hmm\r
\r
this is page data
"""
# sample client receive file
client_recv = """HTTP/1.0 200 Okidoki\r
Host: localhost\r
X-Hobbes: Hmm\r
\r
this is page data
"""

