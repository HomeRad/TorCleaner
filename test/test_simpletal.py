# -*- coding: iso-8859-1 -*-
from StringIO import StringIO
import os, gettext
from wc.webgui.simpletal import simpleTAL, simpleTALES
from wc.webgui import add_default_context
from wc import Name, i18n

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
    context.addGlobal("transe", i18n._("Transe test successful"))
    return context


if __name__=='__main__':
    fp = file(os.path.join(os.getcwd(), "test", "html", "taltest.html"))
    context = get_context()
    print expand_template(fp, context)
