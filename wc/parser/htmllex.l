/* Find recognizable tokens in (probably bad formatted) HTML streams.
   Unrecognizable character data is passed on as a TEXT token. 
*/

%{
#include <string.h>
#include <stdlib.h>
#include "htmlsax.h"

#define YYSTYPE PyObject*
#define YY_EXTRA_TYPE UserData*

#define CLEAR_BUF(a) \
    a = PyMem_Resize(a, char, 1); \
    if (!a) return T_ERROR; \
    a[0] = '\0';

#define SETLVAL \
    PyObject* s = PyString_FromString(yyextra->tmp); \
    if (s==NULL) return T_ERROR; \
    CLEAR_BUF(yyextra->tmp); \
    *yylval = s;

#define ADD_TO_TMP {\
    int len = strlen(yyextra->tmp); \
    yyextra->tmp = PyMem_Resize(yyextra->tmp, char, len+yyleng+1); \
    strncat(yyextra->tmp, yytext, yyleng); \
    }

#include "htmlparse.h"
%}

%option 8bit outfile="htmllex.c"
%option align debug
%option fast
%option nounput nomain noyywrap noyymore noreject
%option reentrant-bison
%option warn
%option never-interactive

%x S_ERROR
%x S_PI
%x S_COMMENT
%x S_DOCTYPE
%x S_CDATA
%x S_TAGSTART
%x S_TAGEND
%x S_SCRIPT
%x S_ATTR1
%x S_ATTR2
%x S_ATTR3
%x S_ATTR4
%x S_ATTR5
%x S_APOSSTRING
%x S_STRING

RX_WHITE_SPACE	[\n\r\ \t\b\012]
RX_EQUAL	=
RX_NAME	[a-zA-Z]([-a-zA-Z0-9_])*

%%

  /*********************** EOF ************************/
<<EOF>> {
    return T_WAIT;
}

  /*********************** COMMENT ************************/
<INITIAL>"<!--" { 
    BEGIN(S_COMMENT);
}

<S_COMMENT>"-->" {
    SETLVAL;
    BEGIN(INITIAL);
    return T_COMMENT;
}

<S_COMMENT>"-" {
    ADD_TO_TMP;
}

<S_COMMENT>[^\-]* {
    ADD_TO_TMP;
}

  /*********************** DOCTYPE ************************/
<INITIAL>"<!DOCTYPE" {
    BEGIN(S_DOCTYPE);
}

<S_DOCTYPE>">" {
    SETLVAL;
    BEGIN(INITIAL);
    return T_DOCTYPE;
}

<S_DOCTYPE>[^\>]* {
    ADD_TO_TMP;
}

  /*********************** CDATA ************************/
<INITIAL>"<![CDATA[" { 
    BEGIN(S_CDATA);
}

<S_CDATA>"]]>" {
    SETLVAL;
    BEGIN(INITIAL);
    return T_CDATA;
}

<S_CDATA>"]" {
    ADD_TO_TMP;
}

<S_CDATA>[^\]]* {
    ADD_TO_TMP;
}

  /*********************** PI ************************/
<INITIAL>"<?" {
    BEGIN(S_PI);
}

<S_PI>"?>" {
    SETLVAL;
    BEGIN(INITIAL);
    return T_PI;
}

<S_PI>[^\?]*|\? {
    ADD_TO_TMP;
}

  /*********************** TAGSTART ************************/
<INITIAL><{RX_WHITE_SPACE}* {
    BEGIN(S_TAGSTART);
}

<S_TAGSTART>{RX_NAME} {
    ADD_TO_TMP;
}

<S_TAGSTART>{RX_WHITE_SPACE}+ {
    char* p = yyextra->tmp;
    while (p) { *p = tolower(*p); p++; }
    yyextra->ltag = PyString_FromString(yyextra->tmp);
    if (!yyextra->ltag) { return T_ERROR; }
    BEGIN(S_ATTR1);
}

<S_TAGSTART>"/>" {
    BEGIN(INITIAL);
    return T_ELEMENT_START_END;
}

<S_TAGSTART>">" {
    if (!strcmp("script", PyString_AS_STRING(yyextra->ltag))) BEGIN(S_SCRIPT);
    else BEGIN(INITIAL);
    return T_ELEMENT_START;
}

<S_TAGSTART>. {
    BEGIN(S_ERROR);
}

  /*********************** SCRIPT ************************/
<S_SCRIPT><\/{RX_WHITE_SPACE}*[Ss][Cc][Rr][Ii][Pp][Tt]{RX_WHITE_SPACE}*> {
    SETLVAL;
    BEGIN(INITIAL);
    return T_SCRIPT;
}

<S_SCRIPT>[^<]*|< {
    ADD_TO_TMP;
}

  /*********************** ATTRS ************************/
<S_ATTR1>{RX_NAME} {
    ADD_TO_TMP;
    BEGIN(S_ATTR2);
}

<S_ATTR1,S_ATTR2>"/>" {
    BEGIN(INITIAL);
    return T_ELEMENT_START_END;
}

<S_ATTR1,S_ATTR2>">" {
    BEGIN(INITIAL);
    return T_ELEMENT_START;
}

<S_ATTR1,S_ATTR2>. {
}

<S_ATTR2>{RX_NAME} {
    ADD_TO_TMP;
}

<S_ATTR2>{RX_WHITE_SPACE}+ {
    BEGIN(S_ATTR3);
}

<S_ATTR2,S_ATTR3>{RX_EQUAL}{RX_WHITE_SPACE}* {
    BEGIN(S_ATTR4);
}

<S_ATTR3>{RX_NAME} {
    // XXX add single attribute
    ADD_TO_TMP;
    BEGIN(S_ATTR2);
}

<S_ATTR4>\" {
    BEGIN(S_STRING);
}


<S_ATTR4>\' {
    BEGIN(S_APOSSTRING);
}


<S_ATTR4>[^\012 \t\b\r\n>\'\"]+ {
    ADD_TO_TMP;
    BEGIN(S_ATTR5);
}

<S_ATTR5>[^\012 \t\b\r\n>]+ {
    ADD_TO_TMP;
}

<S_ATTR5>">" {
    // XXX
    BEGIN(INITIAL);
}

<S_ATTR5>{RX_WHITE_SPACE}+ {
    // XXX
    BEGIN(S_ATTR1);
}

<S_APOSSTRING>\' {
    // XXX
    BEGIN(S_ATTR1);
}

<S_APOSSTRING>[^']* { 
    ADD_TO_TMP;
}


<S_STRING>\" {
    // XXX
    BEGIN(S_ATTR1);
}

<S_STRING>[^"]* { 
    ADD_TO_TMP;
}

  /*********************** TAGEND ************************/
<INITIAL>"</"{RX_WHITE_SPACE} {
    BEGIN(S_TAGEND);
}

<S_TAGEND>{RX_NAME} {
    ADD_TO_TMP;
}

<S_TAGEND>">" {
    SETLVAL;
    return T_ELEMENT_END;
}

<S_TAGEND>"<"{RX_WHITE_SPACE} {
    BEGIN(S_TAGSTART);
}

<S_TAGEND>. {
}

  /*********************** ERROR ************************/
<S_ERROR>[^>]* {
    ADD_TO_TMP;
}

<S_ERROR>">" {
    SETLVAL;
    BEGIN(INITIAL);
    return T_TEXT;
}

  /*********************** END ************************/
%%

int htmllexInit (void** scanner, UserData* data) {
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

