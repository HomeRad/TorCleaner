# -*- coding: iso-8859-1 -*-
import StringIO
import os
import gettext
import wc
import wc.webgui.simpletal.simpleTAL
import wc.webgui.simpletal.simpleTALES

def expand_template (fp, context):
    """expand the given template file in context
       return expanded data"""
    template = wc.webgui.simpletal.simpleTAL.compileHTMLTemplate(fp)
    out = StringIO.StringIO()
    LocaleDir = os.path.join(os.getcwd(), "test", "share", "locale")
    translator = gettext.translation(wc.Name, LocaleDir, ["de"])
    template.expand(context, out, translator=translator)
    return out.getvalue()


def get_context ():
    # init and return TALES context
    context = wc.webgui.simpletal.simpleTALES.Context()
    context.addGlobal("parameter", "hullabulla")
    context.addGlobal("transe", _("Transe test successful"))
    return context


if __name__=='__main__':
    fp = file(os.path.join(os.getcwd(), "test", "html", "taltest.html"))
    context = get_context()
    print expand_template(fp, context)
