from StringIO import StringIO
import sys, os, gettext
from wc.webgui.simpletal import simpleTAL, simpleTALES
from wc import Name

def expand_template (f, context):
    """expand the given template file in context
       return expanded data"""
    template = simpleTAL.compileHTMLTemplate(f)
    out = StringIO()
    LocaleDir = os.path.join(os.getcwd(), "test", "share", "locale")
    translator = gettext.translation(Name, LocaleDir, ["de"])
    template.expand(context, out, translator=translator)
    data = out.getvalue()
    out.close()
    return data


def get_context ():
    # init and return TALES context
    context = simpleTALES.Context()
    context.addGlobal("parameter", "hullabulla")
    return context


f = file(os.path.join(os.getcwd(), "test", "html", "taltest.html"))
print expand_template(f, get_context())
