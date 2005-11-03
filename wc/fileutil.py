# -*- coding: iso-8859-1 -*-
# Copyright (C) 2005  Bastian Kleineidam
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
"""
File and path utilities.
"""

def write_file_save (filename, content, backup=False):
    """
    Overwrite a possibly existing file with new content. Do this
    in a manner that does not leave truncated or broken files behind.
    @param filename: name of file to write
    @type filename: string
    @param content: file content to write
    @type content: string
    @param backup: if backup file should be left
    @type backup: bool
    """
    # first write in a temp file
    f = file(filename+".tmp", 'wb')
    f.write(content)
    f.close()
    # move orig file to backup
    os.rename(filename, filename+".bak")
    # move temp file to orig
    os.rename(filename+".tmp", filename)
    # remove backup
    if not backup:
        os.remove(filename+".bak")

