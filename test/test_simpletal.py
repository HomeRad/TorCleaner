from StringIO import StringIO
import sys, os, gettext
from wc.webgui.simpletal import simpleTAL, simpleTALES
from wc import LocaleDir, Name

def expand_template (f, context):
    """expand the given template file in context
       return expanded data"""
    template = simpleTAL.compileHTMLTemplate(f)
    out = StringIO()
    translator = gettext.translation(Name, LocaleDir, ["de"])
    template.expand(context, out, translator=translator)
    data = out.getvalue()
    out.close()
    return data


def get_context ():
    # make TAL context
    context = simpleTALES.Context()
    context.addGlobal("option", "hullabulla")
    return context


path = "test/html/taltest.html"
f = file(path)
context = get_context()
print expand_template(f, context)
