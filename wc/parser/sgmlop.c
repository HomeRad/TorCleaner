/*
 * SGMLOP
 * $Id$
 *
 * snatched from PyXML
 *
 * The sgmlop accelerator module
 *
 * This module provides a FastSGMLParser type, which is designed to
 * speed up the standard sgmllib and xmllib modules.  The parser can
 * be configured to support either basic SGML (enough of it to process
 * HTML documents, at least) or XML.  This module also provides an
 * Element type, useful for fast but simple DOM implementations.
 *
 * Copyright (c) 1998-2000 by Secret Labs AB
 * Copyright (c) 1998-2000 by Fredrik Lundh
 *
 * fredrik@pythonware.com
 * http://www.pythonware.com
 *
 * By obtaining, using, and/or copying this software and/or its
 * associated documentation, you agree that you have read, understood,
 * and will comply with the following terms and conditions:
 *
 * Permission to use, copy, modify, and distribute this software and its
 * associated documentation for any purpose and without fee is hereby
 * granted, provided that the above copyright notice appears in all
 * copies, and that both that copyright notice and this permission notice
 * appear in supporting documentation, and that the name of Secret Labs
 * AB or the author not be used in advertising or publicity pertaining to
 * distribution of the software without specific, written prior
 * permission.
 *
 * SECRET LABS AB AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO
 * THIS SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND
 * FITNESS.  IN NO EVENT SHALL SECRET LABS AB OR THE AUTHOR BE LIABLE FOR
 * ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
 * WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
 * ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT
 * OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.  */

#include "Python.h"

#include <ctype.h>

/* 8-bit character set */
#define CHAR_T  char
#define ISALNUM isalnum
#define ISSPACE isspace
#define TOLOWER tolower

/* ==================================================================== */
/* parser data type */

/* state flags */
#define MAYBE 1
#define SURE 2

/* parser type definition */
typedef struct {
    PyObject_HEAD

    /* state attributes */
    int feed;
    int shorttag; /* 0=normal 2=parsing shorttag */
    int doctype; /* 0=normal 1=dtd pending 2=parsing dtd */

    /* buffer (holds incomplete tags) */
    char* buffer;
    int bufferlen; /* current amount of data */
    int buffertotal; /* actually allocated */

    /* callbacks */
    PyObject* unknown_starttag;
    PyObject* unknown_endtag;
    PyObject* handle_proc;
    PyObject* handle_special;
    PyObject* handle_charref;
    PyObject* handle_entityref;
    PyObject* handle_data;
    PyObject* handle_cdata;
    PyObject* handle_comment;

} FastSGMLParserObject;

staticforward PyTypeObject FastSGMLParser_Type;

/* forward declarations */
static int fastfeed(FastSGMLParserObject* self);
static PyObject* attrparse(const CHAR_T *p, int len);


/* -------------------------------------------------------------------- */
/* create parser */

static PyObject* _sgmlop_new(PyObject* item) {
    FastSGMLParserObject* self;

    if (!(self=PyObject_NEW(FastSGMLParserObject, &FastSGMLParser_Type)))
	return NULL;

    self->feed = 0;
    self->shorttag = 0;
    self->doctype = 0;
    self->buffer = NULL;
    self->bufferlen = 0;
    self->buffertotal = 0;

    /* register callbacks */
    self->unknown_starttag = PyObject_GetAttrString(item, "unknown_starttag");
    self->unknown_endtag = PyObject_GetAttrString(item, "unknown_endtag");
    self->handle_proc = PyObject_GetAttrString(item, "handle_proc");
    self->handle_special = PyObject_GetAttrString(item, "handle_special");
    self->handle_charref = PyObject_GetAttrString(item, "handle_charref");
    self->handle_entityref = PyObject_GetAttrString(item, "handle_entityref");
    self->handle_data = PyObject_GetAttrString(item, "handle_data");
    self->handle_cdata = PyObject_GetAttrString(item, "handle_cdata");
    self->handle_comment = PyObject_GetAttrString(item, "handle_comment");
    /* PyErr_Clear(); *//* commented out because we dont accept missing
     callbacks! */
    return (PyObject*) self;
}


static PyObject* _sgmlop_sgmlparser(PyObject* self, PyObject* args) {
    PyObject* item;
    if (!PyArg_ParseTuple(args, "O", &item))
	return NULL;
    return _sgmlop_new(item);
}


static void
_sgmlop_dealloc(FastSGMLParserObject* self)
{
    if (self->buffer)
	free(self->buffer);
    Py_DECREF(self->unknown_starttag);
    Py_DECREF(self->unknown_endtag);
    Py_DECREF(self->handle_proc);
    Py_DECREF(self->handle_special);
    Py_DECREF(self->handle_charref);
    Py_DECREF(self->handle_entityref);
    Py_DECREF(self->handle_data);
    Py_DECREF(self->handle_cdata);
    Py_DECREF(self->handle_comment);
    PyMem_DEL(self);
}

/* release the internal buffer and reset all values except the function
 callbacks */
static void reset(FastSGMLParserObject* self) {
    if (self->buffer!=NULL) {
	free(self->buffer);
	self->buffer = NULL;
    }
    self->bufferlen = 0;
    self->buffertotal = 0;
    self->feed = 0;
    self->shorttag = 0;
    self->doctype = 0;
}

/* reset the parser */
static PyObject* _sgmlop_reset(FastSGMLParserObject* self, PyObject* args) {
    if (!PyArg_NoArgs(args))
	return NULL;
    reset(self);
    Py_INCREF(Py_None);
    return Py_None;
}


/* -------------------------------------------------------------------- */
/* feed data to parser.  the parser processes as much of the data as
 possible, and keeps the rest in a local buffer. */

static PyObject*
feed(FastSGMLParserObject* self, char* string, int stringlen, int last)
{
    /* common subroutine for SGMLParser.feed and SGMLParser.close */

    int length;

    if (self->feed) {
	/* dealing with recursive feeds isn't exactly trivial, so
	 let's just bail out before the parser messes things up */
        PyErr_SetString(PyExc_AssertionError, "recursive feed");
        return NULL;
    }

    /* append new text block to local buffer */
    if (!self->buffer) {
	length = stringlen;
	self->buffer = malloc(length);
	self->buffertotal = stringlen;
    } else {
	length = self->bufferlen + stringlen;
	if (length > self->buffertotal) {
	    self->buffer = realloc(self->buffer, length);
	    self->buffertotal = length;
	}
    }
    if (!self->buffer) {
	PyErr_NoMemory();
	return NULL;
    }
    memcpy(self->buffer + self->bufferlen, string, stringlen);
    self->bufferlen = length;

    self->feed = 1;
    length = fastfeed(self);
    self->feed = 0;

    if (length < 0) {
	return NULL;
    }

    if (length > self->bufferlen) {
	/* ran beyond the end of the buffer (internal error)*/
	PyErr_SetString(PyExc_AssertionError, "buffer overrun");
	return NULL;
    }

    if (length > 0 && length < self->bufferlen) {
	/* adjust buffer */
	memmove(self->buffer, self->buffer + length,
		self->bufferlen - length);
    }

    self->bufferlen -= length;

    /* if data remains in the buffer even through this is the
     last call, do an extra handle_data to get rid of it */
    if (last) {
	if (!PyObject_CallFunction(self->handle_data,
				   "s#", self->buffer, self->bufferlen))
	    return NULL;
	/* shut the parser down and release the internal buffers */
	reset(self);
    }

    return Py_BuildValue("i", self->bufferlen);
}

static PyObject*
_sgmlop_feed(FastSGMLParserObject* self, PyObject* args)
{
    /* feed a chunk of data to the parser */
    char* string;
    int stringlen;
    if (!PyArg_ParseTuple(args, "t#", &string, &stringlen))
	return NULL;
    return feed(self, string, stringlen, 0);
}

static PyObject*
_sgmlop_close(FastSGMLParserObject* self, PyObject* args)
{
    /* flush parser buffers */
    if (!PyArg_NoArgs(args))
	return NULL;
    return feed(self, "", 0, 1);
}

static PyObject*
_sgmlop_parse(FastSGMLParserObject* self, PyObject* args)
{
    /* feed a single chunk of data to the parser */
    char* string;
    int stringlen;
    if (!PyArg_ParseTuple(args, "t#", &string, &stringlen))
	return NULL;
    return feed(self, string, stringlen, 1);
}


/* -------------------------------------------------------------------- */
/* type interface */

static PyMethodDef _sgmlop_methods[] = {
    /* incremental parsing */
    {"feed", (PyCFunction) _sgmlop_feed, METH_VARARGS},
    /* reset the parser */
    {"reset", (PyCFunction) _sgmlop_reset, 0},
    {"close", (PyCFunction) _sgmlop_close, 0},
    /* one-shot parsing */
    {"parse", (PyCFunction) _sgmlop_parse, METH_VARARGS},
    {NULL, NULL}
};

static PyObject*
_sgmlop_getattr(FastSGMLParserObject* self, char* name)
{
    return Py_FindMethod(_sgmlop_methods, (PyObject*) self, name);
}

statichere PyTypeObject FastSGMLParser_Type = {
    PyObject_HEAD_INIT(NULL)
	0, /* ob_size */
	"FastSGMLParser", /* tp_name */
	sizeof(FastSGMLParserObject), /* tp_size */
	0, /* tp_itemsize */
	/* methods */
	(destructor)_sgmlop_dealloc, /* tp_dealloc */
	0, /* tp_print */
	(getattrfunc)_sgmlop_getattr, /* tp_getattr */
	0 /* tp_setattr */
};

/* ==================================================================== */
/* python module interface */

static PyMethodDef _functions[] = {
    {"SGMLParser", _sgmlop_sgmlparser, METH_VARARGS},
    {NULL, NULL}
};

void
#ifdef WIN32
__declspec(dllexport)
#endif
initsgmlop(void)
{
    /* Patch object type */
    FastSGMLParser_Type.ob_type = &PyType_Type;
    Py_InitModule("sgmlop", _functions);
}

/* -------------------------------------------------------------------- */
/* the parser does it all in a single loop, keeping the necessary
 state in a few flag variables and the data buffer.  if you have
 a good optimizer, this can be incredibly fast. */

#define TAG 0x100
#define TAG_START 0x101
#define TAG_END 0x102
#define TAG_EMPTY 0x103
#define DIRECTIVE 0x104
#define DOCTYPE 0x105
#define PI 0x106
#define DTD_START 0x107
#define DTD_END 0x108
#define DTD_ENTITY 0x109
#define CDATA 0x200
#define ENTITYREF 0x400
#define CHARREF 0x401
#define COMMENT 0x800

#define INC_P if (++p>=end) goto eol

static int fastfeed(FastSGMLParserObject* self) {
    CHAR_T *end; /* tail */
    CHAR_T *p, *q, *s; /* scanning pointers */
    CHAR_T *b, *t, *e; /* token start/end */

    int token;

    s = q = p = (CHAR_T*) self->buffer;
    end = (CHAR_T*) (self->buffer + self->bufferlen);
    while (p < end) {

	q = p; /* start of token */

	if (*p == '<') {
	    int has_attr=0;

	    /* <tags> */
	    token = TAG_START;
            INC_P;

	    if (*p == '!') {
		/* <! directive */
                INC_P;
		token = DIRECTIVE;
		b = t = p;
		if (*p == '-') {
		    int i;
		    /* <!-- comment --> */
		    token = COMMENT;
		    b = p + 2;
		    for (;;) {
			if (p+3 >= end)
			    goto eol;
			if (p[1] != '-')
			    p += 2; /* boyer moore, sort of ;-) */
			else if (p[0] != '-')
			    p++;
			else {
			    i=2;
			    /* skip spaces */
			    while (isspace(p[i])) {
				++i;
				if (p+i >= end)
				    goto eol;
			    }
			    if (p[i]=='>')
				break;
			    p+=i;
			}
		    }
		    e = p;
		    p += i+1;
		    goto eot;
		}
	    } else if (*p == '?') {
		token = PI;
                INC_P;
	    } else if (*p == '/') {
		/* </endtag> */
		token = TAG_END;
                INC_P;
	    }

	    /* process tag name */
	    b = p;
	    while (ISALNUM(*p) || *p == '-' || *p == '.' ||
		   *p == ':' || *p == '?') {
		*p = (CHAR_T) TOLOWER(*p);
                INC_P;
	    }

	    t = p;

	    if (*p == '/') {
		/* <tag/data/ or <tag/> */
		token = TAG_START;
		e = p;
                INC_P;
		if (*p == '>') {
		    /* <tag/> */
		    token = TAG_EMPTY;
                    INC_P;
		} else
		    /* <tag/data/ */
		    self->shorttag = SURE;
		/* we'll generate an end tag when we stumble upon
		 the end slash */
	    } else {
		/* skip attributes */
		int quote = 0;
		int last = 0;
                int attr_end = 0;
		while (*p!='>' || quote) {
		    if (!ISSPACE(*p)) {
			has_attr = 1;
			if (attr_end==1) {
                            attr_end=2;
			}
			if (quote) {
			    if (*p == quote) {
				quote = 0;
			    }
			}
			else {
			    if (*p=='=') {
				attr_end = 1;
			    }
			    else if (*p=='"' || *p=='\'') {
				quote = *p;
				attr_end = 0;
			    }
                            else if (*p=='[' && self->doctype) {
				self->doctype = SURE;
				token = DTD_START;
				e = p++;
				goto eot;
			    }
			}
		    }
		    else if (attr_end==2) {
                        attr_end=0;
		    }
		    last = *p;
                    INC_P;
		}

		e = p++;

		// attention: it could be <a href=/foo/>bar</a>
                // thats why we have attr_end
		if (last=='/' && !attr_end) {
		    /* note: end tags cannot have attributes! */
                    has_attr=0;
		    /* <tag/> */
		    e--;
		    token = TAG_EMPTY;
                }
		if (token == PI && last == '?')
		    e--;

		if (self->doctype == MAYBE)
		    self->doctype = 0; /* there was no dtd */
	    }
	} // if p=='<'

	else if (*p == '/' && self->shorttag) {

	    /* end of shorttag. this generates an empty end tag */
	    token = TAG_END;
	    self->shorttag = 0;
	    b = t = e = p;
            INC_P;
	}

	else if (*p == ']' && self->doctype) {
	    /* end of dtd. this generates an empty end tag */
	    token = DTD_END;
	    /* FIXME: who handles the ending > !? */
	    b = t = e = p;
            INC_P;
	    self->doctype = 0;
	}

	else if (*p == '%' && self->doctype) {
	    /* doctype entities */
	    token = DTD_ENTITY;
            INC_P;
	    b = t = p;
	    while (ISALNUM(*p) || *p == '.') {
                INC_P;
	    }
	    e = p;
	    if (*p == ';') {
		p++;
	    }
	    else {
		continue;
	    }

	}

	else if (*p == '&') {
	    /* entities */
	    token = ENTITYREF;
            INC_P;
	    if (*p == '#') {
		token = CHARREF;
                INC_P;
	    }
	    b = t = p;
	    while (ISALNUM(*p) || *p == '.') {
		INC_P;
	    }
	    e = p;
	    if (*p == ';') {
		p++;
	    }
	}

	else {
	    /* raw data */
	    if (++p >= end) {
		q = p;
		goto eol;
	    }
	    continue;
	}

    eot: /* end of token */

	if (q != s) {
	    /* flush any raw data before this tag */
	    PyObject* res;
	    res = PyObject_CallFunction(self->handle_data,
					"s#", s, q-s);
	    if (!res)
		return -1;
	    Py_DECREF(res);
	}

	/* invoke callbacks */
	if (token & TAG) {
	    if (token == TAG_END) {
		PyObject* res;
		res = PyObject_CallFunction(self->unknown_endtag,
					    "s#", b, t-b);
		if (!res)
		    return -1;
		Py_DECREF(res);
	    } else if (token == DIRECTIVE || token == DOCTYPE) {
		PyObject* res;
		res = PyObject_CallFunction(self->handle_special,
					    "s#", b, e-b);
		if (!res)
		    return -1;
		Py_DECREF(res);
	    } else if (token == PI) {
		PyObject* res;
		int len = t-b;
		while (ISSPACE(*t))
		    t++;
		res = PyObject_CallFunction(self->handle_proc,
					    "s#s#", b, len, t, e-t);
		if (!res)
		    return -1;
		Py_DECREF(res);
	    } else {
		PyObject* res;
		PyObject* attr;
		int len = t-b;
		while (ISSPACE(*t)) {
		    t++;
		}
		attr = attrparse(t, e-t);
		if (!attr)
		    return -1;
		res = PyObject_CallFunction(self->unknown_starttag,
					    "s#O", b, len, attr);
		Py_DECREF(attr);
		if (!res)
		    return -1;
		Py_DECREF(res);
		if (token == TAG_EMPTY) {
		    res = PyObject_CallFunction(self->unknown_endtag,
						"s#", b, len);
		    if (!res)
			return -1;
		    Py_DECREF(res);
		}
	    }
	} else if (token == ENTITYREF) {
	    PyObject* res;
	    res = PyObject_CallFunction(self->handle_entityref,
					"s#", b, e-b);
	    if (!res)
		return -1;
	    Py_DECREF(res);
	} else if (token == CHARREF) {
	    PyObject* res;
	    res = PyObject_CallFunction(self->handle_charref,
					"s#", b, e-b);
	    if (!res)
		return -1;
	    Py_DECREF(res);
	} else if (token == CDATA) {
	    PyObject* res;
	    res = PyObject_CallFunction(self->handle_cdata,
					"s#", b, e-b);
	    if (!res)
		return -1;
	    Py_DECREF(res);
	} else if (token == COMMENT) {
	    PyObject* res;
	    res = PyObject_CallFunction(self->handle_comment,
					"s#", b, e-b);
	    if (!res)
		return -1;
	    Py_DECREF(res);
	}

	q = p; /* start of token */
	s = p; /* start of span */
    }

eol: /* end of line */
    if (q != s) {
	PyObject* res;
	res = PyObject_CallFunction(self->handle_data,
				    "s#", s, q-s);
	if (!res)
	    return -1;
	Py_DECREF(res);
    }

    /* returns the number of bytes consumed in this pass */
    return ((char*) q) - self->buffer;
}


static PyObject*
attrparse(const CHAR_T* p, int len)
{
    PyObject* attrs;
    PyObject* res;
    PyObject* key = NULL;
    PyObject* value = NULL;
    const CHAR_T* end = p + len;
    const CHAR_T* q;

    attrs = PyList_New(0);

    while (p < end) {

	/* skip leading space */
	while (p < end && ISSPACE(*p))
	    p++;
	if (p >= end)
	    break;

	/* get attribute name (key) */
	q = p;
	while (p < end && *p != '=' && !ISSPACE(*p))
	    p++;

	key = PyString_FromStringAndSize(q, p-q);
	if (key == NULL)
	    goto err;

	value = key; /* in SGML mode, default is same as key */

	Py_INCREF(value);

	while (p < end && ISSPACE(*p))
	    p++;

	if (p < end && *p == '=') {

	    /* attribute value found */
	    Py_DECREF(value);

	    if (p < end) {
		p++;
	    }
	    while (p < end && ISSPACE(*p)) {
		p++;
	    }

	    q = p;
	    if (p < end && (*p == '"' || *p == '\'')) {
		p++;
		while (p < end && *p != *q) {
		    p++;
		}
		value = PyString_FromStringAndSize(q+1, p-q-1);
		if (p < end && *p == *q)
		    p++;
	    } else {
		while (p < end && !ISSPACE(*p)) {
		    p++;
		}
		value = PyString_FromStringAndSize(q, p-q);
	    }

	    if (value == NULL)
		goto err;
	}

	/* add to list */
	res = PyTuple_New(2);
	if (!res)
	    goto err;
	PyTuple_SET_ITEM(res, 0, key);
	PyTuple_SET_ITEM(res, 1, value);
	if (PyList_Append(attrs, res) < 0) {
	    Py_DECREF(res);
	    goto err;
	}
	Py_DECREF(res);
	key = NULL;
	value = NULL;

    }

    return attrs;

err:
    Py_XDECREF(key);
    Py_XDECREF(value);
    Py_DECREF(attrs);
    return NULL;
}
