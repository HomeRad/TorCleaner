#include <libxml/HTMLparser.h>
#include <libxml/parserInternals.h>
#include <libxml/SAX.h>
#include <Python.h>

/* require Python >= 2.0 */
#ifndef PY_VERSION_HEX
#error please install Python >= 2.0
#endif

#if PY_VERSION_HEX < 0x02000000
#error please install Python >= 2.0
#endif

/* windoze thingies  for vsnprintf */
#ifdef WIN32
#ifdef _MSC_VER    /* Microsoft Visual C++ */
#define vsnprintf _vsnprintf
#endif
#ifdef __BORLANDC__ /* Borland C++ Builder */
#if __BORLANDC__ <= 0x0530 /* C++ Builder 3.0 */
#define vsnprintf(a, b, c, d) vsprintf(a, c, d)
#endif
#endif
#ifdef __MINGW32__      /* GCC MingW32 */
#define vsnprintf _vsnprintf
#endif
#endif

/* debugging */
#if 0
#define debug(a) printf(a)
#else
#define debug(a)
#endif

/* user_data type for SAX calls */
typedef struct {
    /* the Python SAX class instance */
    PyObject* handler;
    /* the parser context */
    htmlParserCtxtPtr context;
    /* error flag */
    int error;
    /* stored Python exception (if error occurred) */
    PyObject* exc_type;
    PyObject* exc_val;
    PyObject* exc_tb;
    /* to decode UTF8 we need a buffer */
    unsigned char* buf;
    unsigned int buflen;
} UserData;


/* parser type definition */
typedef struct {
    PyObject_HEAD
    htmlSAXHandlerPtr sax;
    UserData* userData;
} parser_object;


staticforward PyTypeObject parser_type;


/* =========== SAX C --> Python callbacks ========= */
/* The SAX handler requires C functions. The C functions
 * then call the Python handler functions (which must be available
 * in the handler object).
 */

// XXX hack: limiting buffer oversize to 1024 is not pretty
static int encodedStrlen(const xmlChar* value, int len) {
    int extra = (len - xmlUTF8Strlen(value)) * 10;
    debug("encodedStrlen\n");
    if (extra<len) {
	extra = len;
    }
    return extra+1024;
}


static void _internalSubset (void* user_data, const xmlChar* name,
			    const xmlChar* externId, const xmlChar* systemId) {
    UserData* ud = (UserData*) user_data;
    PyObject* callback = PyObject_GetAttrString(ud->handler,
        					"internalSubset");
    PyObject* arglist = Py_BuildValue("(sss)", name, externId, systemId);
    debug("internalSubset\n");
    if (PyEval_CallObject(callback, arglist)==NULL) {
	ud->error = 1;
	PyErr_Fetch(&(ud->exc_type), &(ud->exc_val), &(ud->exc_tb));
    }
    Py_DECREF(arglist);
}


static void _entityDecl (void* user_data, const xmlChar* name, int type,
			const xmlChar* publicId, const xmlChar* systemId,
			xmlChar* content) {
    UserData* ud = (UserData*) user_data;
    PyObject* callback = PyObject_GetAttrString(ud->handler,
						"entityDecl");
    PyObject* arglist = Py_BuildValue("(sisss)", name, type, publicId,
				      systemId, content);
    debug("entityDecl\n");
    if (PyEval_CallObject(callback, arglist)==NULL) {
	ud->error = 1;
	PyErr_Fetch(&(ud->exc_type), &(ud->exc_val), &(ud->exc_tb));
    }
    Py_DECREF(arglist);
}


static void _notationDecl (void* user_data, const xmlChar* name,
			   const xmlChar* publicId, const xmlChar* systemId) {
    UserData* ud = (UserData*) user_data;
    PyObject* callback = PyObject_GetAttrString(ud->handler,
						"notationDecl");
    PyObject* arglist = Py_BuildValue("(sss)", name, publicId, systemId);
    debug("notationDecl\n");
    if (PyEval_CallObject(callback, arglist)==NULL) {
	ud->error = 1;
	PyErr_Fetch(&(ud->exc_type), &(ud->exc_val), &(ud->exc_tb));
    }
    Py_DECREF(arglist);
}


static void _attributeDecl (void* user_data, const xmlChar* elem,
			    const xmlChar* name, int type, int def,
			    const xmlChar* defaultValue,
			    xmlEnumerationPtr tree) {
    UserData* ud = (UserData*) user_data;
    PyObject* callback = PyObject_GetAttrString(ud->handler, "attributeDecl");
    PyObject* arglist;
    PyObject* nameList;
    PyObject* newName;
    xmlEnumerationPtr node;
    int count = 0;
    debug("attributeDecl\n");

    for (node = tree; node!=NULL; node = node->next) {
        count++;
    }
    nameList = PyList_New(count);
    count = 0;
    for (node = tree; node != NULL; node = node->next) {
	newName = PyString_FromString(node->name);
	PyList_SetItem(nameList, count, newName);
        count++;
    }
    arglist = Py_BuildValue("(ssiisO)", elem, name, type, def,
				      defaultValue, nameList);
    if (PyEval_CallObject(callback, arglist)==NULL) {
	ud->error = 1;
	PyErr_Fetch(&(ud->exc_type), &(ud->exc_val), &(ud->exc_tb));
    }
    Py_DECREF(arglist);
}


static void _elementDecl (void* user_data, const xmlChar* name, int type,
			  xmlElementContentPtr content) {
    UserData* ud = (UserData*) user_data;
    PyObject* callback = PyObject_GetAttrString(ud->handler,
						"elementDecl");
    // XXX content object wrapper
    PyObject* arglist = Py_BuildValue("(si)", name, type);
    debug("elementDecl\n");
    if (PyEval_CallObject(callback, arglist)==NULL) {
	ud->error = 1;
	PyErr_Fetch(&(ud->exc_type), &(ud->exc_val), &(ud->exc_tb));
    }
    Py_DECREF(arglist);
}


static void _unparsedEntityDecl (void* user_data, const xmlChar* name,
				const xmlChar* publicId,
				const xmlChar* systemId,
				const xmlChar* notationName) {
    UserData* ud = (UserData*) user_data;
    PyObject* callback = PyObject_GetAttrString(ud->handler,
						"unparsedEntityDecl");
    PyObject* arglist = Py_BuildValue("(ssss)", name, publicId, systemId,
				      notationName);
    debug("unparsedEntityDecl\n");
    if (PyEval_CallObject(callback, arglist)==NULL) {
	ud->error = 1;
	PyErr_Fetch(&(ud->exc_type), &(ud->exc_val), &(ud->exc_tb));
    }
    Py_DECREF(arglist);
}


static void _setDocumentLocator (void* user_data, xmlSAXLocatorPtr loc) {
    UserData* ud = (UserData*) user_data;
    PyObject* callback = PyObject_GetAttrString(ud->handler,
						"setDocumentLocator");
    // XXX locator object wrapper
    PyObject* arglist = Py_BuildValue("(s)", "documentlocator");
    debug("setDocumentLocator\n");
    if (PyEval_CallObject(callback, arglist)==NULL) {
	ud->error = 1;
	PyErr_Fetch(&(ud->exc_type), &(ud->exc_val), &(ud->exc_tb));
    }
    Py_DECREF(arglist);
}


static void _startDocument (void* user_data) {
    UserData* ud = (UserData*) user_data;
    PyObject* callback = PyObject_GetAttrString(ud->handler, "startDocument");
    PyObject* arglist = Py_BuildValue("()");
    debug("startDocument\n");
    if (PyEval_CallObject(callback, arglist)==NULL) {
	ud->error = 1;
	PyErr_Fetch(&(ud->exc_type), &(ud->exc_val), &(ud->exc_tb));
    }
    Py_DECREF(arglist);
}


static void _endDocument (void* user_data) {
    UserData* ud = (UserData*) user_data;
    PyObject* callback = PyObject_GetAttrString(ud->handler, "endDocument");
    PyObject* arglist = Py_BuildValue("()");
    debug("endDocument\n");
    if (PyEval_CallObject(callback, arglist)==NULL) {
	ud->error = 1;
	PyErr_Fetch(&(ud->exc_type), &(ud->exc_val), &(ud->exc_tb));
    }
    Py_DECREF(arglist);
}


static void _startElement (void* user_data, const xmlChar* name,
			  const xmlChar** attrs) {
    UserData* ud = (UserData*) user_data;
    PyObject* callback = PyObject_GetAttrString(ud->handler, "startElement");
    PyObject* arglist;
    PyObject* pyattrs = PyDict_New();
    PyObject* key;
    PyObject* value;
    int i;
    debug("startElement\n");
    if (attrs) {
	for (i=0; attrs[i] != NULL; i++) {
	    key = PyString_FromString(attrs[i]);
	    if (attrs[++i]!=NULL) {
		/* strip leading and ending quotes, which occurs
		 * with invalid HTML
		 */
                int p;
		int len = strlen(attrs[i]);
		// calculate space needed for encoding
		int outlen = encodedStrlen(attrs[i], len);
		if (outlen > ud->buflen) {
		    ud->buf = PyMem_Resize(ud->buf, unsigned char, outlen);
		    ud->buflen = outlen;
		}
		// re-encode entities
		if ((p=htmlEncodeEntities(ud->buf, &outlen, attrs[i], &len, 0))!=0) {
		    ud->exc_type = PyExc_ValueError;
		    if (p==-2) {
			ud->exc_val = PyString_FromString("htmlEncodeEntities: transcoding error");
		    }
		    else {
			ud->exc_val = PyString_FromString("htmlEncodeEntities: internal error");
		    }
		    ud->exc_tb = NULL;
		    return;
		}
                p = 0;
		if (outlen > 1) {
		    if (ud->buf[outlen-1]=='"' || ud->buf[outlen-1]=='\'') {
			outlen--;
		    }
		    if (ud->buf[0]=='"' || ud->buf[0]=='\'') {
			p++;
                        outlen--;
		    }
		}
		value = PyString_FromStringAndSize(ud->buf + p, outlen);
	    }
	    else {
		Py_INCREF(Py_None);
                value = Py_None;
	    }
            PyDict_SetItem(pyattrs, key, value);
	}
    }
    arglist = Py_BuildValue("(sO)", name, pyattrs);
    if (PyEval_CallObject(callback, arglist)==NULL) {
	ud->error = 1;
	PyErr_Fetch(&(ud->exc_type), &(ud->exc_val), &(ud->exc_tb));
    }
    Py_DECREF(arglist);
}


static void _endElement (void* user_data, const xmlChar* name) {
    debug("endElement\n");
    /* ignore invalid HTML endtags */
    if (xmlStrEqual(name,"area") ||
	xmlStrEqual(name,"base") ||
        xmlStrEqual(name,"basefont") ||
	xmlStrEqual(name,"br") ||
	xmlStrEqual(name,"col") ||
	xmlStrEqual(name,"frame") ||
	xmlStrEqual(name,"hr") ||
	xmlStrEqual(name,"img") ||
	xmlStrEqual(name,"input") ||
	xmlStrEqual(name,"isindex") ||
	xmlStrEqual(name,"link") ||
        xmlStrEqual(name,"meta") ||
	xmlStrEqual(name,"param")) {
	return;
    }
    else {
	UserData* ud = (UserData*) user_data;
	PyObject* callback = PyObject_GetAttrString(ud->handler,
						    "endElement");
	PyObject* arglist = Py_BuildValue("(s)", name);
	if (PyEval_CallObject(callback, arglist)==NULL) {
	    ud->error = 1;
	    PyErr_Fetch(&(ud->exc_type), &(ud->exc_val), &(ud->exc_tb));
	}
	Py_DECREF(arglist);
    }
}


static void _reference (void* user_data, const xmlChar* name) {
    UserData* ud = (UserData*) user_data;
    PyObject* callback = PyObject_GetAttrString(ud->handler, "reference");
    PyObject* arglist = Py_BuildValue("(s)", name);
    debug("reference\n");
    if (PyEval_CallObject(callback, arglist)==NULL) {
	ud->error = 1;
	PyErr_Fetch(&(ud->exc_type), &(ud->exc_val), &(ud->exc_tb));
    }
    Py_DECREF(arglist);
}


static void _characters (void* user_data, const xmlChar* ch, int len) {
    UserData* ud = (UserData*) user_data;
    PyObject* callback = PyObject_GetAttrString(ud->handler, "characters");
    PyObject* arglist;
    int i;
    // calculate space needed for encoding
    int outlen = encodedStrlen(ch, len);
    debug("characters\n");
    if (outlen > ud->buflen) {
        ud->buf = PyMem_Resize(ud->buf, unsigned char, outlen);
        ud->buflen = outlen;
    }
    // re-encode entities
    if ((i=htmlEncodeEntities(ud->buf, &outlen, ch, &len, 0))!=0) {
	ud->exc_type = PyExc_ValueError;
	if (i==-2) {
	    ud->exc_val = PyString_FromString("htmlEncodeEntities: transcoding error");
	}
	else {
            ud->exc_val = PyString_FromString("htmlEncodeEntities: internal error");
	}
        ud->exc_tb = NULL;
        return;
    }
    arglist = Py_BuildValue("(s#)", ud->buf, outlen);
    if (PyEval_CallObject(callback, arglist)==NULL) {
	ud->error = 1;
	PyErr_Fetch(&(ud->exc_type), &(ud->exc_val), &(ud->exc_tb));
    }
    Py_DECREF(arglist);
}


static void _ignorableWhitespace (void* user_data, const xmlChar* ch, int len) {
    UserData* ud = (UserData*) user_data;
    PyObject* callback = PyObject_GetAttrString(ud->handler,
						"ignorableWhitespace");
    PyObject* arglist = Py_BuildValue("(s#)", ch, len);
    debug("ignorableWhitespace\n");
    if (PyEval_CallObject(callback, arglist)==NULL) {
	ud->error = 1;
	PyErr_Fetch(&(ud->exc_type), &(ud->exc_val), &(ud->exc_tb));
    }
    Py_DECREF(arglist);
}


static void _processingInstruction (void* user_data, const xmlChar* target,
				   const xmlChar* data) {
    UserData* ud = (UserData*) user_data;
    PyObject* callback = PyObject_GetAttrString(ud->handler,
						"processingInstruction");
    PyObject* arglist = Py_BuildValue("(ss)", target, data);
    debug("processingInstruction\n");
    if (PyEval_CallObject(callback, arglist)==NULL) {
	ud->error = 1;
	PyErr_Fetch(&(ud->exc_type), &(ud->exc_val), &(ud->exc_tb));
    }
    Py_DECREF(arglist);
}


static void _comment (void* user_data, const xmlChar* value) {
    UserData* ud = (UserData*) user_data;
    PyObject* callback = PyObject_GetAttrString(ud->handler, "comment");
    PyObject* arglist;
    int len = strlen(value), i;
    // calculate space needed for encoding
    int outlen = encodedStrlen(value, len);
    debug("comment\n");
    if (outlen > ud->buflen) {
        ud->buf = PyMem_Resize(ud->buf, unsigned char, outlen);
        ud->buflen = outlen;
    }
    if ((i=UTF8ToHtml(ud->buf, &outlen, value, &len))!=0) {
	ud->exc_type = PyExc_ValueError;
	if (i==-2) {
	    ud->exc_val = PyString_FromString("UTF8ToHtml: transcoding error");
	}
	else {
            ud->exc_val = PyString_FromString("UTF8ToHtml: internal error");
	}
        ud->exc_tb = NULL;
        return;
    }
    arglist = Py_BuildValue("(s#)", ud->buf, outlen);
    if (PyEval_CallObject(callback, arglist)==NULL) {
	ud->error = 1;
	PyErr_Fetch(&(ud->exc_type), &(ud->exc_val), &(ud->exc_tb));
    }
    Py_DECREF(arglist);
}


static void _warning (void* user_data, const char* msg, ...) {
    UserData* ud = (UserData*) user_data;
    PyObject* callback = PyObject_GetAttrString(ud->handler, "warning");
    PyObject* arglist;
    va_list args;
    int line = getLineNumber(ud->context);
    int col = getColumnNumber(ud->context);
    debug("warning\n");
    if (ud->buflen < 1024) {
	ud->buf = PyMem_Resize(ud->buf, unsigned char, 1024);
        ud->buflen = 1024;
    }
    va_start(args, msg);
    vsnprintf(ud->buf, 1024, msg, args);
    va_end(args);
    arglist = Py_BuildValue("(iis)", line, col, ud->buf);
    if (PyEval_CallObject(callback, arglist)==NULL) {
	ud->error = 1;
	PyErr_Fetch(&(ud->exc_type), &(ud->exc_val), &(ud->exc_tb));
    }
    Py_DECREF(arglist);
}


static void _error (void* user_data, const char* msg, ...) {
    UserData* ud = (UserData*) user_data;
    PyObject* callback = PyObject_GetAttrString(ud->handler, "error");
    PyObject* arglist;
    va_list args;
    int line = getLineNumber(ud->context);
    int col = getColumnNumber(ud->context);
    debug("error\n");
    if (ud->buflen < 1024) {
	ud->buf = PyMem_Resize(ud->buf, unsigned char, 1024);
        ud->buflen = 1024;
    }
    va_start(args, msg);
    vsnprintf(ud->buf, 1024, msg, args);
    va_end(args);
    arglist = Py_BuildValue("(iis)", line, col, ud->buf);
    if (PyEval_CallObject(callback, arglist)==NULL) {
	ud->error = 1;
	PyErr_Fetch(&(ud->exc_type), &(ud->exc_val), &(ud->exc_tb));
    }
    Py_DECREF(arglist);
}


static void _fatalError (void* user_data, const char* msg, ...) {
    UserData* ud = (UserData*) user_data;
    PyObject* callback = PyObject_GetAttrString(ud->handler, "fatalError");
    PyObject* arglist;
    va_list args;
    int line = getLineNumber(ud->context);
    int col = getColumnNumber(ud->context);
    debug("fatalError\n");
    if (ud->buflen < 1024) {
	ud->buf = PyMem_Resize(ud->buf, unsigned char, 1024);
        ud->buflen = 1024;
    }
    va_start(args, msg);
    vsnprintf(ud->buf, 1024, msg, args);
    va_end(args);
    arglist = Py_BuildValue("(iis)", line, col, ud->buf);
    if (PyEval_CallObject(callback, arglist)==NULL) {
	ud->error = 1;
	PyErr_Fetch(&(ud->exc_type), &(ud->exc_val), &(ud->exc_tb));
    }
    Py_DECREF(arglist);
}


static void _cdataBlock (void* user_data, const xmlChar* ch, int len) {
    UserData* ud = (UserData*) user_data;
    PyObject* callback = PyObject_GetAttrString(ud->handler, "cdataBlock");
    PyObject* arglist;
    int i;
    // calculate space needed for encoding
    int outlen = encodedStrlen(ch, len);
    debug("cdataBlock\n");
    if (outlen > ud->buflen) {
        ud->buf = PyMem_Resize(ud->buf, unsigned char, outlen);
        ud->buflen = outlen;
    }
    if ((i=UTF8ToHtml(ud->buf, &outlen, ch, &len))!=0) {
	ud->exc_type = PyExc_ValueError;
	if (i==-2) {
	    ud->exc_val = PyString_FromString("UTF8ToHtml: transcoding error");
	}
	else {
            ud->exc_val = PyString_FromString("UTF8ToHtml: internal error");
	}
        ud->exc_tb = NULL;
        return;
    }
    arglist = Py_BuildValue("(s#)", ud->buf, outlen);
    if (PyEval_CallObject(callback, arglist)==NULL) {
	ud->error = 1;
	PyErr_Fetch(&(ud->exc_type), &(ud->exc_val), &(ud->exc_tb));
    }
    Py_DECREF(arglist);
}


static void _externalSubset (void* user_data, const xmlChar* name,
			    const xmlChar* externalID,
			    const xmlChar* systemID) {
    UserData* ud = (UserData*) user_data;
    PyObject* callback = PyObject_GetAttrString(ud->handler,
						"externalSubset");
    PyObject* arglist = Py_BuildValue("(sss)", name, externalID, systemID);
    debug("externalSubset\n");
    if (PyEval_CallObject(callback, arglist)==NULL) {
	ud->error = 1;
	PyErr_Fetch(&(ud->exc_type), &(ud->exc_val), &(ud->exc_tb));
    }
    Py_DECREF(arglist);
}


/* create parser */
static PyObject* htmlsax_parser(PyObject* self, PyObject* args) {
    PyObject* handler;
    parser_object* p;
    if (!PyArg_ParseTuple(args, "O", &handler)) {
	PyErr_SetString(PyExc_TypeError, "SAX2 handler object arg required");
	return NULL;
    }

    if (!(p=PyObject_NEW(parser_object, &parser_type))) {
	return NULL;
    }
    p->userData = PyMem_New(UserData, sizeof(UserData));
    p->userData->handler = handler;

    p->sax = PyMem_New(htmlSAXHandler, sizeof(htmlSAXHandler));
    memset(p->sax, 0, sizeof(htmlSAXHandler));
    /* register SAX callbacks */
    p->sax->internalSubset     = PyObject_HasAttrString(handler, "internalSubset") ? _internalSubset : NULL;
    p->sax->entityDecl         = PyObject_HasAttrString(handler, "entityDecl") ? _entityDecl : NULL;
    p->sax->notationDecl       = PyObject_HasAttrString(handler, "notationDecl") ? _notationDecl : NULL;
    p->sax->attributeDecl      = PyObject_HasAttrString(handler, "attributeDecl") ? _attributeDecl : NULL;
    p->sax->elementDecl        = PyObject_HasAttrString(handler, "elementDecl") ? _elementDecl : NULL;
    p->sax->unparsedEntityDecl = PyObject_HasAttrString(handler, "unparsedEntityDecl") ? _unparsedEntityDecl : NULL;
    p->sax->setDocumentLocator = PyObject_HasAttrString(handler, "setDocumentLocator") ? _setDocumentLocator : NULL;
    p->sax->startDocument      = PyObject_HasAttrString(handler, "startDocument") ? _startDocument : NULL;
    p->sax->endDocument        = PyObject_HasAttrString(handler, "endDocument") ? _endDocument : NULL;
    p->sax->startElement       = PyObject_HasAttrString(handler, "startElement") ? _startElement : NULL;
    p->sax->endElement         = PyObject_HasAttrString(handler, "endElement") ? _endElement : NULL;
    p->sax->reference          = PyObject_HasAttrString(handler, "reference") ? _reference : NULL;
    p->sax->characters            = PyObject_HasAttrString(handler, "characters") ? _characters : NULL;
    p->sax->ignorableWhitespace   = PyObject_HasAttrString(handler, "ignorableWhitespace") ? _ignorableWhitespace : NULL;
    p->sax->processingInstruction = PyObject_HasAttrString(handler, "processingInstruction") ? _processingInstruction : NULL;
    p->sax->comment            = PyObject_HasAttrString(handler, "comment") ? _comment : NULL;
    p->sax->warning            = PyObject_HasAttrString(handler, "warning") ? _warning : NULL;
    p->sax->error              = PyObject_HasAttrString(handler, "error") ? _error : NULL;
    p->sax->fatalError         = PyObject_HasAttrString(handler, "fatalError") ? _fatalError : NULL;
    p->sax->cdataBlock         = PyObject_HasAttrString(handler, "cdataBlock") ? _cdataBlock : NULL;
    p->sax->externalSubset     = PyObject_HasAttrString(handler, "externalSubset") ? _externalSubset : NULL;
    p->userData->context =
	htmlCreatePushParserCtxt(p->sax, /* the SAX handler */
				 p->userData, /* our user_data */
				 NULL, /* chunk of data */
				 0, /* size of chunk */
				 NULL, /* filename (optional) */
				 XML_CHAR_ENCODING_8859_1 /* encoding */
				);
    p->userData->error = 0;
    p->userData->exc_type = NULL;
    p->userData->exc_val = NULL;
    p->userData->exc_tb = NULL;
    p->userData->buf = NULL;
    p->userData->buflen = 0;
    return (PyObject*) p;
}


static void parser_dealloc(parser_object* self)
{
    htmlFreeParserCtxt(self->userData->context);
    PyMem_Del(self->userData->buf);
    PyMem_Del(self->userData);
    PyMem_Del(self->sax);
    PyMem_DEL(self);
}


static PyObject* parser_flush(parser_object* self, PyObject* args) {
    /* flush parser buffers */
    int res=0;
    debug("flush\n");
    if (!PyArg_ParseTuple(args, "")) {
	PyErr_SetString(PyExc_TypeError, "no args required");
        return NULL;
    }
    self->userData->exc_type = NULL;
    self->userData->exc_val = NULL;
    self->userData->exc_tb = NULL;

    res = htmlParseChunk(self->userData->context, NULL, 0, 1);
    if (self->userData->error!=0) {
        self->userData->error = 0;
        if (self->userData->exc_type!=NULL) {
            /* note: we give away these objects, so dont decref */
            PyErr_Restore(self->userData->exc_type,
        		  self->userData->exc_val,
        		  self->userData->exc_tb);
        }
        return NULL;
    }
    return Py_BuildValue("i", res);
}


static PyObject* parser_feed(parser_object* self, PyObject* args) {
    /* feed a chunk of data to the parser */
    int res=0, slen;
    const char* s;
    debug("feed\n");
    if (!PyArg_ParseTuple(args, "t#", &s, &slen)) {
	PyErr_SetString(PyExc_TypeError, "string arg required");
	return NULL;
    }
    self->userData->exc_type = NULL;
    self->userData->exc_val = NULL;
    self->userData->exc_tb = NULL;

    res = htmlParseChunk(self->userData->context, s, slen, 0);
    if (self->userData->error!=0) {
        self->userData->error = 0;
        if (self->userData->exc_type!=NULL) {
	    /* note: we give away these objects, so dont decref */
            PyErr_Restore(self->userData->exc_type,
        		  self->userData->exc_val,
        		  self->userData->exc_tb);
        }
        return NULL;
    }
    return Py_BuildValue("i", res);
}


static PyObject* parser_reset(parser_object* self, PyObject* args) {
    if (!PyArg_ParseTuple(args, "")) {
	PyErr_SetString(PyExc_TypeError, "no args required");
	return NULL;
    }
    htmlFreeParserCtxt(self->userData->context);
    self->userData->context =
	htmlCreatePushParserCtxt(self->sax,
				 self->userData,
				 NULL,
				 0,
				 NULL,
				 XML_CHAR_ENCODING_8859_1);
    Py_INCREF(Py_None);
    return Py_None;
}


/* type interface */

static PyMethodDef parser_methods[] = {
    /* incremental parsing */
    {"feed",  (PyCFunction) parser_feed, METH_VARARGS},
    /* reset the parser (no flushing) */
    {"reset", (PyCFunction) parser_reset, METH_VARARGS},
    /* flush the parser buffers */
    {"flush", (PyCFunction) parser_flush, METH_VARARGS},
    {NULL, NULL}
};


static PyObject* parser_getattr(parser_object* self, char* name) {
    return Py_FindMethod(parser_methods, (PyObject*) self, name);
}


statichere PyTypeObject parser_type = {
    PyObject_HEAD_INIT(NULL)
    0, /* ob_size */
    "parser", /* tp_name */
    sizeof(parser_object), /* tp_size */
    0, /* tp_itemsize */
    /* methods */
    (destructor)parser_dealloc, /* tp_dealloc */
    0, /* tp_print */
    (getattrfunc)parser_getattr, /* tp_getattr */
    0 /* tp_setattr */
};


/* python module interface */

static PyMethodDef htmlsax_methods[] = {
    {"parser", htmlsax_parser, METH_VARARGS},
    {NULL, NULL}
};


/* initialization of the htmlsaxhtmlop module */

void inithtmlsax(void) {
    Py_InitModule("htmlsax", htmlsax_methods);
}

