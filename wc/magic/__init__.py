# -*- coding: iso-8859-1 -*-
"""magic(5) module"""

import os
import wc
import magic

_magic = None

def classify (fp):
    """classify given file"""
    global _magic
    if not _magic:
        # initialize mime data
        magicfile = os.path.join(wc.ConfigDir, "magic.mime")
        assert os.path.exists(magicfile)
        magiccache = magicfile+".mgc"
        _magic = magic.Magic(magicfile, magiccache)
    return _magic.classify(fp)
