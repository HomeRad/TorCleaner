from StringIO import StringIO
import sys, os
try:
    from wc.webgui.simpletal import simpleTAL, simpleTALES
    raise SystemExit("Global WebCleaner installation found")
except ImportError:
    sys.path.insert(0, os.getcwd())
    from wc.webgui.simpletal import simpleTAL, simpleTALES

def expand_template (f, context):
    """expand the given template file in context
       return expanded data"""
    template = simpleTAL.compileHTMLTemplate(f)
    out = StringIO()
    template.expand(context, out)
    data = out.getvalue()
    out.close()
    return data


def get_context ():
    # make TAL context
    return simpleTALES.Context()


path = "test/html/taltest.html"
f = file(path)
context = get_context()
print expand_template(f, context)
