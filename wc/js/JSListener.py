# -*- coding: iso-8859-1 -*-
"""JavaScript engine listener"""

#  BFilter - a smart ad-filtering web proxy
#  Copyright (C) 2002-2003  Joseph Artsimovich <joseph_a@mail.ru>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

# Ported from C++ to Python by Bastian Kleineidam <calvin@users.sf.net>

__version__ = "$Revision$"[11:-2]
__date__    = "$Date$"[7:-2]

class JSListener (object):
    """Define handler functions for javascript events"""

    def jsProcessData (self, data):
        """handler for document.write content"""
        raise NotImplementedError("abstract method jsProcessData")

    def jsProcessPopup (self):
        """handler for popup windows"""
        raise NotImplementedError("abstract method jsProcessPopup")

    def jsProcessError (self, msg):
        """handler for syntax errors"""
        raise NotImplementedError("abstract method jsProcessError")
