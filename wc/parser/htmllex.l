/* Find recognizable tokens in (probably bad formatted) HTML streams.
   Unrecognizable character data is passed on as a TEXT token. 
*/

%{
#include <string.h>
#include <stdlib.h>
#include "htmlsax.h"

#define YYSTYPE PyObject*
#define YY_EXTRA_TYPE UserData*
#define SETLVAL \
    PyObject* s = PyString_FromStringAndSize(yytext, yyleng); \
    fprintf(stderr, "Hui: %p\n", s); \
    if (s==NULL) { \
        return EOF; \
    } \
    else *yylval = s

#include "htmlparse.h"
%}

%option 8bit outfile="htmllex.c"
%option debug
%option align
%option fast
%option nounput nomain noyywrap noyymore noreject
%option reentrant-bison
%option warn
%option never-interactive

/* The INNER state represents all possibilities between any two angle
 * brackets <  INNER >
 */
%x S_INNER
/* we saw an EQUAL sign after a name, now we can be any where until the
 * next bit of whitespace (unquoted)
 */
%x S_ATTRVAL
/* PIs do recognize a name, then possibly some text */
%x S_PI
/* collect the rest of the PI if there is any */
%x S_PI_COLLECT
%x S_COMMENT
%x S_DOCTYPE
%x S_CDATA
/* capture a string bounded by apostrophes "'" Aka single quotes
 * Ignore things like double quotes
 */
%x S_APOSSTRING
/* capture a string bounded by double quotes
 * Ignore things like single quotes
 */
%x S_STRING
/**
 * Try to recover from some scanner unmatch. Scan ahead for a closing '>'
 */
%x S_ERROR_RECOVER

RX_WHITE_SPACE	[\n\r\ \t\b\012]
RX_EQUAL	=
RX_NAME	[a-zA-Z]([-a-zA-Z0-9_])*

%%

<INITIAL><<EOF>> {
    return EOF;
}

<INITIAL>"</" {
    BEGIN(S_INNER);
    return T_ANGLE_END_OPEN;
}

<INITIAL>"<!--" { 
    BEGIN(S_COMMENT);
    return T_COMMENT_START;
}


<INITIAL>"<!DOCTYPE" {  
    BEGIN(S_DOCTYPE);
    return T_DOCTYPE_START;
}

<INITIAL>"<![CDATA[" { 
    BEGIN(S_CDATA);
    return T_CDATA_START;
}

<INITIAL>"<?" { 
    BEGIN(S_PI);
    return T_PI_OPEN;
}

<INITIAL>"<" {
    SETLVAL;
    BEGIN(S_INNER);
    return T_ANGLE_OPEN;
}

<INITIAL>[^<]+ {
    SETLVAL;
    return T_TEXT;
}


<S_INNER>"/>" {
    BEGIN(INITIAL);
    return T_ANGLE_END_CLOSE;
}

<S_INNER>">" {
    SETLVAL;
    BEGIN(INITIAL);
    return T_ANGLE_CLOSE;
}

<S_INNER>{RX_EQUAL} {
    BEGIN(S_ATTRVAL);
    return T_EQUAL;
}

<S_INNER>{RX_NAME} {
    SETLVAL;
    return T_NAME;
}

<S_INNER>{RX_WHITE_SPACE}* {
    /* ignore whitespace */
}


<S_ATTRVAL>\" {
    BEGIN(S_STRING);
}


<S_ATTRVAL>\' {
    BEGIN(S_APOSSTRING);
}


<S_ATTRVAL>[^ \t\r\n>\'\"]+ {
    SETLVAL;
    BEGIN(S_INNER);
    return T_NAME;
}

<S_ATTRVAL>">" { 
    BEGIN(INITIAL);
    return T_ANGLE_CLOSE;
}

<S_ATTRVAL>[ \t\r\n]* {
    SETLVAL;
}



<S_PI>{RX_NAME} {
    SETLVAL;
    BEGIN(S_PI_COLLECT);
    return T_NAME;
}

<S_PI_COLLECT>"?>" { 
    BEGIN(INITIAL);
    return T_PI_CLOSE;
}

<S_PI_COLLECT>[^?]* { 
    SETLVAL;
    return T_TEXT;
}


<S_COMMENT>"-->" {
    BEGIN(INITIAL);
    return T_COMMENT_END;
}

<S_COMMENT>"-" {
    /* handle any hanging minus signs E.g. i - 2; --a; etc. */
    SETLVAL;
    return T_TEXT;
}

<S_COMMENT>[^\-]* {
    SETLVAL;
    return T_TEXT;
}

<S_CDATA>"]]>" {
    BEGIN(INITIAL);
    return T_CDATA_END;
}

<S_CDATA>"]" {
    SETLVAL;
    return T_TEXT;
}

<S_CDATA>[^\]]* {
    SETLVAL;
    return T_TEXT;
}

<S_DOCTYPE>">" {
    BEGIN(INITIAL);
    return T_ANGLE_CLOSE;
}

<S_DOCTYPE>[^\>]* {
    SETLVAL;
    return T_TEXT;
}


<S_APOSSTRING>\' {
    BEGIN(S_INNER);
    return T_STRING;
}

<S_APOSSTRING>[^']* { 
    SETLVAL;
    return T_VALUE;
}


<S_STRING>\" {
    BEGIN(S_INNER);
    return T_STRING;
}

<S_STRING>[^"]* { 
    SETLVAL;
    return T_VALUE;
}


<S_ERROR_RECOVER>">" {
    SETLVAL;
    BEGIN(INITIAL);
    return T_ANGLE_CLOSE;
}


<S_ERROR_RECOVER>[^>]* {
    /* ignore all this till recover */
    SETLVAL;
    return T_TEXT;
}

%%

int htmllexInit (void** scanner, const char* s, int slen, UserData* data) {
    yylex_init(scanner);
    yyset_extra(data, *scanner);
    return 0;
}

int htmllexStart (void* scanner, const char* s, int slen) {
    yy_scan_bytes(s, slen, scanner);
    return 0;
}

int htmllexStop (void* scanner) {
    yylex_destroy(scanner);
    return 0;
}

