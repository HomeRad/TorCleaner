# -*- coding: iso-8859-1 -*-
from StringIO import StringIO
import os, gettext
from wc.webgui.simpletal import simpleTAL, simpleTALES
from wc.webgui import add_default_context
from wc import Name

def expand_template (fp, context):
    """expand the given template file in context
       return expanded data"""
    template = simpleTAL.compileHTMLTemplate(fp)
    out = StringIO()
    LocaleDir = os.path.join(os.getcwd(), "test", "share", "locale")
    translator = gettext.translation(Name, LocaleDir, ["de"])
    template.expand(context, out, translator=translator)
    return out.getvalue()


def get_context ():
    # init and return TALES context
    context = simpleTALES.Context()
    context.addGlobal("parameter", "hullabulla")
    return context


fp = file(os.path.join(os.getcwd(), "test", "html", "taltest.html"))
context = get_context()
print expand_template(fp, context)
