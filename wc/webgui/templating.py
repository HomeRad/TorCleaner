import sys, cgi, urllib, os, re, os.path, time, errno

# if you test this, call 'python wc/webgui/templating.py'
if __name__=='__main__':
    sys.path.insert(0, os.getcwd())

# _ for i18n, TemplateDir is the directory with all TAL templates
from wc import _, TemplateDir

try:
    import cPickle as pickle
except ImportError:
    import pickle
try:
    import cStringIO as StringIO
except ImportError:
    import StringIO
try:
    import StructuredText
except ImportError:
    StructuredText = None

# bring in the templating support
from wc.webgui.PageTemplates import PageTemplate
from wc.webgui.PageTemplates.Expressions import getEngine
from wc.webgui.TAL.TALInterpreter import TALInterpreter
from wc.webgui import ZTUtils

def test ():
    filename = os.path.join(TemplateDir, "blocked.html")
    fp = file(filename)
    pt = PageTemplate.PageTemplate()
    pt.id = filename
    pt.pt_edit(fp, 'text/html')
    print pt.pt_render(extra_context={'title': 'Blocked by WebCleaner'})


if __name__=='__main__':
    test()
