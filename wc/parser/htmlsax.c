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

/* user_data type for SAX calls */
typedef struct {
    PyObject* handler;
    htmlParserCtxtPtr context;
    int error;
    PyObject* exc_type;
    PyObject* exc_val;
    PyObject* exc_tb;
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

/* to encode in UTF8->latin1 we need a buffer */
#define ENC_BUF_LEN 1024
static unsigned char encbuf[ENC_BUF_LEN];


static void _internalSubset (void* user_data, const xmlChar* name,
			    const xmlChar* externId, const xmlChar* systemId) {
    //UserData* ud = (UserData*) user_data;
    //PyObject* callback = PyObject_GetAttrString(ud->handler,
    //    					"internalSubset");
}

//static xmlEntity entity;
//static char* entityname;


//static xmlEntityPtr getEntity(void *user_data, const xmlChar *name) {
//    entityname = PyMem_Resize(entityname, char, strlen(name));
//    entity.name = entityname;
//    return &entity;
//}


static void _entityDecl (void* user_data, const xmlChar* name, int type,
			const xmlChar* publicId, const xmlChar* systemId,
			xmlChar* content) {
    UserData* ud = (UserData*) user_data;
    PyObject* callback = PyObject_GetAttrString(ud->handler,
						"entityDecl");
    PyObject* arglist = Py_BuildValue("(sisss)", name, type, publicId,
				      systemId, content);
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
    PyObject* callback = PyObject_GetAttrString(ud->handler,
						"attributeDecl");
    PyObject* arglist;
    PyObject* nameList;
    PyObject* newName;
    xmlEnumerationPtr node;
    int count = 0;

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
    //UserData* ud = (UserData*) user_data;
    //PyObject* callback = PyObject_GetAttrString(ud->handler,
    //    					"elementDecl");
    //PyObject* obj = newXmlelementcontentobject(content);
    //PyObject* arglist = Py_BuildValue("(siO)", name, type, obj);
    //PyEval_CallObject(callback, arglist);
    //Py_DECREF(arglist);
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
    if (PyEval_CallObject(callback, arglist)==NULL) {
	ud->error = 1;
	PyErr_Fetch(&(ud->exc_type), &(ud->exc_val), &(ud->exc_tb));
    }
    Py_DECREF(arglist);
}


static void _setDocumentLocator (void* user_data, xmlSAXLocatorPtr loc) {
    //UserData* ud = (UserData*) user_data;
    //PyObject* callback = PyObject_GetAttrString(ud->handler,
    //    					"setDocumentLocator");
    //locatorobject* locatorObject = newlocatorobject(ud->context, loc);
    //PyObject* arglist = Py_BuildValue("(O)", locatorObject);
    //PyEval_CallObject(callback, arglist);
    //Py_DECREF(arglist);
}


static void _startDocument (void* user_data) {
    UserData* ud = (UserData*) user_data;
    PyObject* callback = PyObject_GetAttrString(ud->handler,
						"startDocument");
    PyObject* arglist = Py_BuildValue("()");
    if (PyEval_CallObject(callback, arglist)==NULL) {
	ud->error = 1;
	PyErr_Fetch(&(ud->exc_type), &(ud->exc_val), &(ud->exc_tb));
    }
    Py_DECREF(arglist);
}


static void _endDocument (void* user_data) {
    UserData* ud = (UserData*) user_data;
    PyObject* callback = PyObject_GetAttrString(ud->handler,
						"endDocument");
    PyObject* arglist = Py_BuildValue("()");
    if (PyEval_CallObject(callback, arglist)==NULL) {
	ud->error = 1;
	PyErr_Fetch(&(ud->exc_type), &(ud->exc_val), &(ud->exc_tb));
    }
    Py_DECREF(arglist);
}


static void _startElement (void* user_data, const xmlChar* name,
			  const xmlChar** attrs) {
    UserData* ud = (UserData*) user_data;
    PyObject* callback = PyObject_GetAttrString(ud->handler,
						"startElement");
    PyObject* arglist;
    PyObject* pyattrs = PyDict_New();
    PyObject* key;
    PyObject* value;
    int i;
    if (attrs) {
	for (i=0; attrs[i] != NULL; i++) {
	    key = PyString_FromString(attrs[i]);
	    if (attrs[++i]!=NULL) {
		/* strip leading and ending quotes, which occurs
		 * with invalid HTML
		 */
                int p = 0;
		int len = strlen(attrs[i]);
		if (len > 1) {
		    if (attrs[i][len-1]=='"' || attrs[i][len-1]=='\'') {
			len--;
		    }
		    if (attrs[i][0]=='"' || attrs[i][0]=='\'') {
			p++;
                        len--;
		    }
		}
		value = PyString_FromStringAndSize(attrs[i]+p, len);
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
    PyObject* callback = PyObject_GetAttrString(ud->handler,
						"reference");
    PyObject* arglist = Py_BuildValue("(s)", name);
    if (PyEval_CallObject(callback, arglist)==NULL) {
	ud->error = 1;
	PyErr_Fetch(&(ud->exc_type), &(ud->exc_val), &(ud->exc_tb));
    }
    Py_DECREF(arglist);
}


static void _characters (void* user_data, const xmlChar* ch, int len) {
    UserData* ud = (UserData*) user_data;
    PyObject* callback = PyObject_GetAttrString(ud->handler,
						"characters");
    PyObject* arglist;
    int outlen = ENC_BUF_LEN;
    // re-encode entities
    htmlEncodeEntities(encbuf, &outlen, ch, &len, 0);
    arglist = Py_BuildValue("(s#)", encbuf, outlen);
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
    if (PyEval_CallObject(callback, arglist)==NULL) {
	ud->error = 1;
	PyErr_Fetch(&(ud->exc_type), &(ud->exc_val), &(ud->exc_tb));
    }
    Py_DECREF(arglist);
}


static void _comment (void* user_data, const xmlChar* value) {
    UserData* ud = (UserData*) user_data;
    PyObject* callback = PyObject_GetAttrString(ud->handler,
						"comment");
    int outlen = ENC_BUF_LEN;
    int len = xmlUTF8Strlen(value);
    PyObject* arglist;
    UTF8ToHtml(encbuf, &outlen, value, &len);
    arglist = Py_BuildValue("(s#)", encbuf, outlen);
    if (PyEval_CallObject(callback, arglist)==NULL) {
	ud->error = 1;
	PyErr_Fetch(&(ud->exc_type), &(ud->exc_val), &(ud->exc_tb));
    }
    Py_DECREF(arglist);
}


static void _warning (void* user_data, const char* msg, ...) {
    UserData* ud = (UserData*) user_data;
    PyObject* callback = PyObject_GetAttrString(ud->handler,
						"warning");
    PyObject* arglist;
    va_list args;
    int line = getLineNumber(ud->context);
    int col = getColumnNumber(ud->context);
    char* buf = PyMem_New(char, 1024);
    va_start(args, msg);
    vsnprintf(buf, 1024, msg, args);
    va_end(args);
    arglist = Py_BuildValue("(iis)", line, col, buf);
    if (PyEval_CallObject(callback, arglist)==NULL) {
	ud->error = 1;
	PyErr_Fetch(&(ud->exc_type), &(ud->exc_val), &(ud->exc_tb));
    }
    Py_DECREF(arglist);
    PyMem_Del(buf);
}


static void _error (void* user_data, const char* msg, ...) {
    UserData* ud = (UserData*) user_data;
    PyObject* callback = PyObject_GetAttrString(ud->handler,
						"error");
    PyObject* arglist;
    va_list args;
    int line = getLineNumber(ud->context);
    int col = getColumnNumber(ud->context);
    char* buf = PyMem_New(char, 1024);
    va_start(args, msg);
    vsnprintf(buf, 1024, msg, args);
    va_end(args);
    arglist = Py_BuildValue("(iis)", line, col, buf);
    if (PyEval_CallObject(callback, arglist)==NULL) {
	ud->error = 1;
	PyErr_Fetch(&(ud->exc_type), &(ud->exc_val), &(ud->exc_tb));
    }
    Py_DECREF(arglist);
    PyMem_Del(buf);
}


static void _fatalError (void* user_data, const char* msg, ...) {
    UserData* ud = (UserData*) user_data;
    PyObject* callback = PyObject_GetAttrString(ud->handler,
						"fatalError");
    PyObject* arglist;
    va_list args;
    int line = getLineNumber(ud->context);
    int col = getColumnNumber(ud->context);
    char* buf = PyMem_New(char, 1024);
    va_start(args, msg);
    vsnprintf(buf, 1024, msg, args);
    va_end(args);
    arglist = Py_BuildValue("(iis)", line, col, buf);
    if (PyEval_CallObject(callback, arglist)==NULL) {
	ud->error = 1;
	PyErr_Fetch(&(ud->exc_type), &(ud->exc_val), &(ud->exc_tb));
    }
    Py_DECREF(arglist);
    PyMem_Del(buf);
}


static void _cdataBlock (void* user_data, const xmlChar* ch, int len) {
    UserData* ud = (UserData*) user_data;
    PyObject* callback = PyObject_GetAttrString(ud->handler,
						"cdataBlock");
    int outlen = ENC_BUF_LEN;
    PyObject* arglist;
    if (UTF8ToHtml(encbuf, &outlen, ch, &len)!=0) {
        // XXX
    }
    arglist = Py_BuildValue("(s#)", encbuf, outlen);
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
    if (PyEval_CallObject(callback, arglist)==NULL) {
	ud->error = 1;
	PyErr_Fetch(&(ud->exc_type), &(ud->exc_val), &(ud->exc_tb));
    }
    Py_DECREF(arglist);
}

#undef ENC_BUF_LEN


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
    /* register SAX callbacks */
    p->sax->internalSubset     = PyObject_HasAttrString(handler, "internalSubset") ? _internalSubset : NULL;
    p->sax->isStandalone       = NULL;
    p->sax->hasInternalSubset  = NULL;
    p->sax->hasExternalSubset  = NULL;
    p->sax->resolveEntity      = NULL;
    p->sax->getEntity          = NULL;
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
    p->sax->getParameterEntity = NULL;
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
    return (PyObject*) p;
}


static void parser_dealloc(parser_object* self)
{
    htmlFreeParserCtxt(self->userData->context);
    PyMem_Del(self->userData);
    PyMem_Del(self->sax);
    PyMem_DEL(self);
}


static PyObject* parser_flush(parser_object* self, PyObject* args) {
    /* flush parser buffers */
    int res;
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
    int res, slen;
    char* s;
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
    //memset(&entity, 0, sizeof(xmlEntity));
    //entityname = NULL;
    Py_InitModule("htmlsax", htmlsax_methods);
}

