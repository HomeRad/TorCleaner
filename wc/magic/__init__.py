# -*- coding: iso-8859-1 -*-
"""magic(5) module"""

import os


_magic = None

def classify (fp):
    """classify given file"""
    global _magic
    if not _magic:
        # initialize mime data
        from magic import Magic
        from wc import ConfigDir
        magicfile = os.path.join(ConfigDir, "magic.mime")
        assert os.path.exists(magicfile)
        magiccache = magicfile+".mgc"
        _magic = Magic(magicfile, magiccache)
    return _magic.classify(fp)
