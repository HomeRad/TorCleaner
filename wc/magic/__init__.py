# -*- coding: iso-8859-1 -*-
"""magic(5) module"""

_magic = None

def classify (fp):
    """classify file fp"""
    global _magic
    if not _magic:
        # initialize mime data
        from magic import Magic
        from wc import ConfigDir
        import os
        magicfile = os.path.join(ConfigDir, "magic.mime")
        magiccache = magicfile+".mgc"
        _magic = Magic(magicfile, magiccache)
    return _magic.classify(fp)
