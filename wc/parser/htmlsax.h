#ifndef HTMLSAX_H
#define HTMLSAX_H

#include "Python.h"

/* require Python >= 2.0 */
#ifndef PY_VERSION_HEX
#error please install Python >= 2.0
#endif

#if PY_VERSION_HEX < 0x02000000
#error please install Python >= 2.0
#endif

/* user_data type for SAX calls */
typedef struct {
    /* the Python SAX class instance to issue callbacks */
    PyObject* handler;
    /* buffer to store scanned but still unparsed characters */
    char* buf;
    /* temporary vars */
    char* tmp;
    PyObject* ltag;
    PyObject* attrname;
    PyObject* attrval;
    PyObject* attrs;
    /* stored Python exception (if error occurred) */
    PyObject* exc_type;
    PyObject* exc_val;
    PyObject* exc_tb;
} UserData;

#endif
