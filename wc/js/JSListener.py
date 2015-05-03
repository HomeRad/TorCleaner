# -*- coding: iso-8859-1 -*-
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
"""
JavaScript engine listener.
"""
from ..decorators import notimplemented


class JSListener(object):
    """
    Define handler functions for javascript events.
    """

    @notimplemented
    def js_process_data(self, data):
        """
        Handler for document.write content.
        """
        pass

    @notimplemented
    def js_process_popup(self):
        """
        Handler for popup windows.
        """
        pass

    @notimplemented
    def js_process_error(self, msg):
        """
        Handler for syntax errors.
        """
        pass
