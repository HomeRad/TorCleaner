%{

/* lhtml.l: source code for libhtmlparse parser
   Mooneer Salem <mooneer@translator.cx> 

   used and adapted for WebCleaner by
   Bastian Kleineidam <calvin@users.sourceforge.net>
   I ripped some of the code structure from sgmlop.c parser,
   which is written by Fredrik Lundh <fredrik@pythonware.com>
*/

#include <string.h>
#include <Python.h>

/* require Python >= 2.0 */
#ifndef PY_VERSION_HEX
#error please install Python >= 2.0
#endif

#if PY_VERSION_HEX < 0x02000000
#error please install Python >= 2.0
#endif

#define LHTML_EOF -128
#define CFREE(a) PyMem_Del(a); a=NULL
#define PFREE(a) Py_DECREF(a); a=NULL
#define XCFREE(a) if (a) { PyMem_Del(a); a=NULL; }
#define XPFREE(a) if (a) { Py_DECREF(a); a=NULL; }
#define yyterminate() return YY_NULL
/*
#define DEBUG
*/
#ifdef DEBUG
#define _debug fprintf(stderr, "state %d yytext %s\n", YYSTATE, yytext)
#else
#define _debug
#endif

/* on Linux: strncasecmp
   on Windows: StrCmpIN ?
   on other: ??
   
   so, here the glibc 2.2.4 code
*/
int my_strncasecmp(const char* s1, const char* s2, int n) {
    const unsigned char* p1 = (const unsigned char*) s1;
    const unsigned char* p2 = (const unsigned char*) s2;
    unsigned char c1, c2;

    if (p1 == p2 || n == 0)
        return 0;

    do {
        c1 = tolower(*p1++);
        c2 = tolower(*p2++);
        if (c1 == '\0' || c1 != c2)
	    return c1 - c2;
    } while (--n > 0);

    return c1 - c2;
}

int htmlopwrap (void) {
    return 1;
}

/* parser type definition */

typedef struct {
    PyObject_HEAD

    /* flex state */
    int state;
    
    /* temporary values for parsing */
    char* tag;
    char* paramname;
    PyObject* params;

    /* callbacks */
    PyObject* handle_starttag;
    PyObject* handle_endtag;
    PyObject* handle_decl;
    PyObject* handle_xmldecl;
    PyObject* handle_ref;
    PyObject* handle_data;
    PyObject* handle_comment;

} parser_object;

staticforward PyTypeObject parser_type;

/* pass the parser object to the scanner */
#define YY_DECL int html_scan (parser_object* self)

%}

%option 8bit

%x COMMENT
%x SCRIPT
%x STARTTAG
%x PARAM
%x PARAM2
%x DECLTAG
%x DPARAM
%x XMLTAG
%x XPARAM
%x XPARAM2
%x ENTITY
%x ENDTAG

%%

<INITIAL><<EOF>>        {
    _debug;
    return LHTML_EOF;
}

<INITIAL>\&[^;\r\n\t <]+/[; \r\n\t<]+	{
    _debug;
    PyObject_CallFunction(self->handle_ref, "s", yytext+1);
    BEGIN(ENTITY);
}

<ENTITY>[; \r\n\t<]+	{
    char *tmp = yytext + strlen(yytext) - 1;
    int i;
    _debug;
    for (i = strlen(tmp) - 1; i >= 0; i--) {
        if (*(tmp+i) != ';') {
	    unput(*(tmp+i));
	}
    }
    BEGIN(INITIAL);
}

<INITIAL><\/[^>]+/>    {
    /* strip tag chars and whitespace */
    int i=2, j;
    _debug;
    while (*(yytext+i) != '\0' && isspace(*(yytext+i))) i++;
    j=i;
    while (*(yytext+j) != '\0' && !isspace(*(yytext+j))) j++;
    PyObject_CallFunction(self->handle_endtag, "s#", yytext+i, j-i);
    BEGIN(ENDTAG);
}

<ENDTAG>>	{
    _debug;
    BEGIN(INITIAL);
}

<INITIAL><!--   {
    _debug;
    self->tag = PyMem_Resize(self->tag, char, 1);
    self->tag[0] = '\0';
    BEGIN(COMMENT);
}

<INITIAL><![ \n\r\t]*	{
    _debug;
    self->params = PyList_New(0);
    BEGIN(DECLTAG);
}

<INITIAL><[ \n\r\t]*    {
    _debug;
    self->params = PyList_New(0);
    BEGIN(STARTTAG);
}

<INITIAL><\?[ \n\r\t]*   {
    _debug;
    self->params = PyList_New(0);
    BEGIN(XMLTAG);
}

<INITIAL>[^<]*  {
    _debug;
    PyObject_CallFunction(self->handle_data, "s", yytext);
}

<SCRIPT><\/[sS][cC][rR][iI][pP][tT][ \r\n\t]*> {
    _debug;
    PyObject_CallFunction(self->handle_endtag, "s", "script");
    BEGIN(INITIAL);
}

<SCRIPT>[^<]+|< {
    _debug;
    PyObject_CallFunction(self->handle_data, "s", yytext);
}

<COMMENT>--[ \r\n\t]*>    {
    _debug;
    PyObject_CallFunction(self->handle_comment, "s", self->tag);
    CFREE(self->tag);
    BEGIN(INITIAL);
}

<COMMENT>[^-]+|"-"       {
    int len = strlen(self->tag);
    _debug;
    self->tag = PyMem_Resize(self->tag, char, len + strlen(yytext) + 1);
    strncpy(self->tag + len, yytext, strlen(yytext));
    self->tag[len+strlen(yytext)] = '\0';
}

<STARTTAG>[^ >\r\n\t]+  {
    char* tmp;
    int len = self->tag ? strlen(self->tag) : 0;
    _debug;
    self->tag = PyMem_Resize(self->tag, char, len + strlen(yytext) + 1);
    strncpy(self->tag + len, yytext, strlen(yytext));
    self->tag[len + strlen(yytext)] = '\0';
    tmp = self->tag;
}

<STARTTAG>">"   {
    int n;
    _debug;
    if (!self->tag) {
        self->tag = PyMem_New(char, 1);
	self->tag[0] = '\0';
    }
    if (self->tag[strlen(self->tag)-1]=='/') {
        /* no parameters allowed for this construct */
        PyObject_CallFunction(self->handle_starttag, "sO", self->tag, PyList_New(0));
	PyObject_CallFunction(self->handle_endtag, "s", self->tag);
    }
    else {
        PyObject_CallFunction(self->handle_starttag, "sO", self->tag, self->params);
    }
    n = strlen(self->tag);
    if (n==6 && my_strncasecmp(self->tag, "script", n)==0) {
        BEGIN(SCRIPT);
    }
    else {
        BEGIN(INITIAL);
    }
    CFREE(self->tag);
    PFREE(self->params);
}

<STARTTAG>[ \r\n\t]+    {
    _debug;
    BEGIN(PARAM);
}

<PARAM>[^ \r\n\t=>]+    {
    _debug;
    self->paramname = PyMem_Resize(self->paramname, char, strlen(yytext)+1);
    strncpy(self->paramname, yytext, strlen(yytext));
    self->paramname[strlen(yytext)] = '\0';
}

<PARAM>">"      {
    int n;
    _debug;
    if (self->paramname) {
        PyList_Append(self->params, Py_BuildValue("sO", self->paramname, Py_None));
	CFREE(self->paramname);
    }
    if (self->tag[strlen(self->tag)-1]=='/') {
        /* no parameters allowed for this construct */
        PyObject_CallFunction(self->handle_starttag, "sO", self->tag, PyList_New(0));
	PyObject_CallFunction(self->handle_endtag, "s", self->tag);
    }
    else {
        PyObject_CallFunction(self->handle_starttag, "sO", self->tag, self->params);
    }
    n = strlen(self->tag);
    if (n>=6 && my_strncasecmp(self->tag, "script", n)==0) {
        BEGIN(SCRIPT);
    }
    else {
        BEGIN(INITIAL);
    }
    CFREE(self->tag);
    PFREE(self->params);
}

<PARAM>[ \r\n\t]*=      {
    _debug;
    if (!self->paramname) {
        /* the empty param name as default, for things like <a =1 =2> */
        self->paramname = PyMem_New(char, 1);
        self->paramname[0] = '\0';
    }
    BEGIN(PARAM2);
}

<PARAM>[ \r\n\t]+       {
    _debug;
    if (self->paramname) {
        PyList_Append(self->params, Py_BuildValue("sO", self->paramname, Py_None));
    }
}

<PARAM2>\"([^"]|\\\")+\"/[ \r\n\t>]   {
    _debug;
    PyList_Append(self->params, Py_BuildValue("ss#", self->paramname, yytext+1, strlen(yytext)-2));
    CFREE(self->paramname);
    BEGIN(PARAM);
}

<PARAM2>\'([^']|\\\')+\'/[ \r\n\t>]   {
    _debug;
    PyList_Append(self->params, Py_BuildValue("ss#", self->paramname, yytext+1, strlen(yytext)-2));
    CFREE(self->paramname);
    BEGIN(PARAM);
}

<PARAM2>[ \r\n\t]+       {
    _debug;
    CFREE(self->paramname);
    BEGIN(PARAM);
}

<PARAM2>[^ \r\n\t>]+    {
    int i=0;
    int j=strlen(yytext)-1;
    _debug;
    /* strip optional quotes, for things like <a b="c> */
    if (yytext[i]=='\'' || yytext[i]=='"') i++;
    if (yytext[j]=='\'' || yytext[j]=='"') j--;
    PyList_Append(self->params, Py_BuildValue("ss#", self->paramname, yytext+i, j-i+1));
    CFREE(self->paramname);
    BEGIN(PARAM);
}

<PARAM2>">" {
    int n;
    _debug;
    /* this occurs with <a b=> */
    PyList_Append(self->params, Py_BuildValue("ss#", self->paramname, yytext+1, strlen(yytext)-2));
    CFREE(self->paramname);
    if (self->tag[strlen(self->tag)-1]=='/') {
        /* no parameters allowed for this construct */
        PyObject_CallFunction(self->handle_starttag, "sO", self->tag, PyList_New(0));
	PyObject_CallFunction(self->handle_endtag, "s", self->tag);
    }
    else {
        PyObject_CallFunction(self->handle_starttag, "sO", self->tag, self->params);
    }
    n = strlen(self->tag);
    if (n>=6 && my_strncasecmp(self->tag, "script", n)==0) {
        BEGIN(SCRIPT);
    }
    else {
        BEGIN(INITIAL);
    }
    CFREE(self->tag);
    PFREE(self->params);
}

<DECLTAG>[^ >\r\n\t]+  {
    char* tmp;
    int len = self->tag ? strlen(self->tag) : 0;
    _debug;
    self->tag = PyMem_Resize(self->tag, char, len + strlen(yytext) + 1);
    strncpy(self->tag + len, yytext, strlen(yytext));
    self->tag[len + strlen(yytext)] = '\0';
    tmp = self->tag;
}

<DECLTAG>">"   {
    _debug;
    if (!self->tag) {
        self->tag = PyMem_New(char, 1);
	self->tag[0] = '\0';
    }
    PyObject_CallFunction(self->handle_decl, "sO", self->tag, self->params);
    CFREE(self->tag);
    PFREE(self->params);
    BEGIN(INITIAL);
}

<DECLTAG>[ \r\n\t]+    {
    _debug;
    BEGIN(DPARAM);
}

<DPARAM>[^ \r\n\t>]+    {
    _debug;
    self->paramname = PyMem_Resize(self->paramname, char, strlen(yytext)+1);
    strncpy(self->paramname, yytext, strlen(yytext));
    self->paramname[strlen(yytext)] = '\0';
}

<DPARAM>">"      {
    _debug;
    if (self->paramname) {
        PyList_Append(self->params, Py_BuildValue("sO", self->paramname, Py_None));
	CFREE(self->paramname);
    }
    PyObject_CallFunction(self->handle_decl, "sO", self->tag, self->params);
    CFREE(self->tag);
    PFREE(self->params);
    BEGIN(INITIAL);
}

<DPARAM>[ \r\n\t]+       {
    _debug;
    if (self->paramname) {
        PyList_Append(self->params, Py_BuildValue("sO", self->paramname, Py_None));
    }
}

<XMLTAG>[^ >\r\n\t]+  {
    char* tmp;
    int len = self->tag ? strlen(self->tag) : 0;
    _debug;
    self->tag = PyMem_Resize(self->tag, char, len + strlen(yytext) + 1);
    strncpy(self->tag + len, yytext, strlen(yytext));
    self->tag[len + strlen(yytext)] = '\0';
    tmp = self->tag;
}

<XMLTAG>\?>   {
    _debug;
    if (!self->tag) {
        self->tag = PyMem_New(char, 1);
	self->tag[0] = '\0';
    }
    PyObject_CallFunction(self->handle_xmldecl, "sO", self->tag, self->params);
    CFREE(self->tag);
    PFREE(self->params);
    BEGIN(INITIAL);
}

<XMLTAG>[ \r\n\t]+    {
    _debug;
    BEGIN(XPARAM);
}

<XPARAM>[^ \r\n\t=>]+    {
    _debug;
    self->paramname = PyMem_Resize(self->paramname, char, strlen(yytext)+1);
    strncpy(self->paramname, yytext, strlen(yytext));
    self->paramname[strlen(yytext)] = '\0';
}

<XPARAM>\?>      {
    _debug;
    if (self->paramname) {
        PyList_Append(self->params, Py_BuildValue("sO", self->paramname, Py_None));
	CFREE(self->paramname);
    }
    PyObject_CallFunction(self->handle_xmldecl, "sO", self->tag, self->params);
    CFREE(self->tag);
    PFREE(self->params);
    BEGIN(INITIAL);
}

<XPARAM>[ \r\n\t]*=      {
    _debug;
    if (!self->paramname) {
        /* the empty param name as default, for things like <a =1 =2> */
        self->paramname = PyMem_New(char, 1);
        self->paramname[0] = '\0';
    }
    BEGIN(XPARAM2);
}

<XPARAM>[ \r\n\t]+       {
    _debug;
    if (self->paramname) {
        PyList_Append(self->params, Py_BuildValue("sO", self->paramname, Py_None));
    }
}

<XPARAM2>\"([^"]|\\\")+\"       {
    _debug;
    PyList_Append(self->params, Py_BuildValue("ss#", self->paramname, yytext+1, strlen(yytext)-2));
    CFREE(self->paramname);
    BEGIN(XPARAM);
}

<XPARAM2>\'([^']|\\')+\'       {
    _debug;
    PyList_Append(self->params, Py_BuildValue("ss#", self->paramname, yytext+1, strlen(yytext)-2));
    CFREE(self->paramname);
    BEGIN(XPARAM);
}

<XPARAM2>[ \r\n\t]+      {
    _debug;
    CFREE(self->paramname);
    BEGIN(XPARAM);
}

<XPARAM2>[^ \r\n\t>?]+    {
    _debug;
    PyList_Append(self->params, Py_BuildValue("ss#", self->paramname, yytext, strlen(yytext)-1));
    CFREE(self->paramname);
    BEGIN(XPARAM);
}

%%

/* create parser */
static PyObject* htmlop_parser(PyObject* self, PyObject* args) {
    PyObject* item;
    parser_object* p;
    if (!PyArg_ParseTuple(args, "O", &item)) {
	return NULL;
    }

    if (!(p=PyObject_NEW(parser_object, &parser_type))) {
	return NULL;
    }

    p->state = 0;
    p->tag = NULL;
    p->paramname = NULL;
    p->params = NULL;

    /* register callbacks */
    p->handle_starttag = PyObject_GetAttrString(item, "handle_starttag");
    p->handle_endtag = PyObject_GetAttrString(item, "handle_endtag");
    p->handle_decl = PyObject_GetAttrString(item, "handle_decl");
    p->handle_xmldecl = PyObject_GetAttrString(item, "handle_xmldecl");
    p->handle_ref = PyObject_GetAttrString(item, "handle_ref");
    p->handle_data = PyObject_GetAttrString(item, "handle_data");
    p->handle_comment = PyObject_GetAttrString(item, "handle_comment");
    /* dont PyErr_Clear(); because we dont accept missing callbacks! */
    return (PyObject*) p;
}


static void parser_dealloc(parser_object* self)
{
    if (self->tag) {
       PyMem_Del(self->tag);
    }
    if (self->paramname) {
        PyMem_Del(self->paramname);
    }
    Py_XDECREF(self->params);
    Py_DECREF(self->handle_starttag);
    Py_DECREF(self->handle_endtag);
    Py_DECREF(self->handle_decl);
    Py_DECREF(self->handle_xmldecl);
    Py_DECREF(self->handle_ref);
    Py_DECREF(self->handle_data);
    Py_DECREF(self->handle_comment);
    PyMem_DEL(self);
}


static PyObject* parser_flush(parser_object* self, PyObject* args) {
    /* flush parser buffers */
    if (!PyArg_ParseTuple(args, "")) {
        return NULL;
    }
    /*
       Because we did not store previous data we have to look at 
       the current state and the temp vars.
    */
    switch(self->state) {
    case STARTTAG:
    case PARAM:
    case PARAM2:
        if (!self->tag) {
            self->tag = PyMem_New(char, 1);
	    self->tag[0] = '\0';
        }
        if (!self->params) {
            self->params = PyList_New(0);
        }
        if (self->tag[strlen(self->tag)-1]=='/') {
            /* no parameters allowed for this construct */
            PyObject_CallFunction(self->handle_starttag, "sO", self->tag, PyList_New(0));
            PyObject_CallFunction(self->handle_endtag, "s", self->tag);
        }
        else {
            PyObject_CallFunction(self->handle_starttag, "sO", self->tag, self->params);
        }
	break;
    case DECLTAG:
    case DPARAM:
        if (!self->tag) {
            self->tag = PyMem_New(char, 1);
	    self->tag[0] = '\0';
        }
        PyObject_CallFunction(self->handle_decl, "sO", self->tag, self->params);
        break;
    case XMLTAG:
    case XPARAM:
    case XPARAM2:
        if (!self->tag) {
            self->tag = PyMem_New(char, 1);
	    self->tag[0] = '\0';
        }
        if (!self->params) {
            self->params = PyList_New(0);
        }
        PyObject_CallFunction(self->handle_xmldecl, "sO", self->tag, self->params);
        break;
    case COMMENT:
        if (!self->tag) {
            self->tag = PyMem_New(char, 1);
	    self->tag[0] = '\0';
        }
        PyObject_CallFunction(self->handle_comment, "s", self->tag);
	break;
    default:
        break;
    }
    Py_INCREF(Py_None);
    return Py_None;
}


static PyObject* parser_feed(parser_object* self, PyObject* args) {
    /* feed a chunk of data to the parser */
    char* s;
    int slen;
    YY_BUFFER_STATE bufstate;
    if (!PyArg_ParseTuple(args, "t#", &s, &slen)) {
	return NULL;
    }
    bufstate = htmlop_scan_bytes(s, slen);
    if (self->state != YYSTATE) {
        BEGIN(self->state);
    }
    html_scan(self);
    self->state = YYSTATE;
    htmlop_delete_buffer(bufstate);
    Py_INCREF(Py_None);
    return Py_None;
}


static PyObject* parser_reset(parser_object* self, PyObject* args) {
    if (!PyArg_ParseTuple(args, "")) {
	return NULL;
    }
    XCFREE(self->tag);
    XCFREE(self->paramname);
    XPFREE(self->params);
    self->state = INITIAL;
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

static PyMethodDef htmlop_methods[] = {
    {"parser", htmlop_parser, METH_VARARGS},
    {NULL, NULL}
};


/* initialization of the htmlop module */

void inithtmlop(void) {
    Py_InitModule("htmlop", htmlop_methods);
}
