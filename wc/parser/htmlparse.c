/* A Bison parser, made from htmlparse.y
   by GNU bison 1.35.  */

#define YYBISON 1  /* Identify Bison output.  */

# define	T_TEXT	257
# define	T_EOF	258
# define	T_COMMENT_START	259
# define	T_COMMENT_END	260
# define	T_ANGLE_OPEN	261
# define	T_ANGLE_CLOSE	262
# define	T_ANGLE_END_CLOSE	263
# define	T_ANGLE_END_OPEN	264
# define	T_NAME	265
# define	T_EQUAL	266
# define	T_VALUE	267
# define	T_QUOTE	268
# define	T_APOS	269
# define	T_PI_OPEN	270
# define	T_PI_CLOSE	271
# define	T_CDATA_START	272
# define	T_CDATA_END	273
# define	T_DOCTYPE_START	274

#line 2 "htmlparse.y"

/* SAX parser, optimized for WebCleaner */
#include <malloc.h>
#include <string.h>
#include <stdio.h>
#include "htmlsax.h"

#define YYSTYPE PyObject*
#define YYPARSE_PARAM scanner
#define YYLEX_PARAM scanner
extern int htmllexInit(void** scanner, void* data);
extern int htmllexStart(void* scanner, const char* s, int slen);
extern int htmllexStop(void* scanner);
extern int yylex(YYSTYPE* yylvalp, void* scanner);
extern void* yyget_extra(void*);
extern void* yyget_lval(void*);
#define YYERROR_VERBOSE 1
extern char* stpcpy(char* src, const char* dest);
int yyerror(char* msg);
PyObject* quote_string (PyObject* val);

/* parser type definition */
typedef struct {
    PyObject_HEAD
    UserData* userData;
    void* scanner;
} parser_object;

staticforward PyTypeObject parser_type;

#ifndef YYSTYPE
# define YYSTYPE int
# define YYSTYPE_IS_TRIVIAL 1
#endif
#ifndef YYDEBUG
# define YYDEBUG 0
#endif



#define	YYFINAL		51
#define	YYFLAG		-32768
#define	YYNTBASE	21

/* YYTRANSLATE(YYLEX) -- Bison token number corresponding to YYLEX. */
#define YYTRANSLATE(x) ((unsigned)(x) <= 274 ? yytranslate[x] : 33)

/* YYTRANSLATE[YYLEX] -- Bison token number corresponding to YYLEX. */
static const char yytranslate[] =
{
       0,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     1,     3,     4,     5,
       6,     7,     8,     9,    10,    11,    12,    13,    14,    15,
      16,    17,    18,    19,    20
};

#if YYDEBUG
static const short yyprhs[] =
{
       0,     0,     2,     5,     7,     9,    11,    13,    15,    17,
      19,    21,    25,    27,    30,    35,    40,    44,    45,    48,
      54,    60,    65,    70,    74,    76,    81,    85,    89,    90,
      93
};
static const short yyrhs[] =
{
      22,     0,    21,    22,     0,    25,     0,    26,     0,    23,
       0,    29,     0,    30,     0,    32,     0,     3,     0,     4,
       0,     5,    24,     6,     0,     3,     0,    24,     3,     0,
       7,    11,    27,     8,     0,     7,    11,    27,     9,     0,
      10,    11,     8,     0,     0,    28,    27,     0,    11,    12,
      14,    13,    14,     0,    11,    12,    15,    13,    15,     0,
      11,    12,    14,    14,     0,    11,    12,    15,    15,     0,
      11,    12,    11,     0,    11,     0,    16,    11,     3,    17,
       0,    16,    11,    17,     0,    18,    31,    19,     0,     0,
      31,     3,     0,    20,     3,     8,     0
};

#endif

#if YYDEBUG
/* YYRLINE[YYN] -- source line where rule number YYN was defined. */
static const short yyrline[] =
{
       0,    62,    63,    67,    68,    69,    70,    71,    72,    73,
      94,    98,   122,   123,   131,   156,   190,   218,   227,   256,
     283,   310,   334,   358,   378,   402,   424,   448,   471,   480,
     494
};
#endif


#if (YYDEBUG) || defined YYERROR_VERBOSE

/* YYTNAME[TOKEN_NUM] -- String name of the token TOKEN_NUM. */
static const char *const yytname[] =
{
  "$", "error", "$undefined.", "T_TEXT", "T_EOF", "T_COMMENT_START", 
  "T_COMMENT_END", "T_ANGLE_OPEN", "T_ANGLE_CLOSE", "T_ANGLE_END_CLOSE", 
  "T_ANGLE_END_OPEN", "T_NAME", "T_EQUAL", "T_VALUE", "T_QUOTE", "T_APOS", 
  "T_PI_OPEN", "T_PI_CLOSE", "T_CDATA_START", "T_CDATA_END", 
  "T_DOCTYPE_START", "elements", "element", "comment", "comment_text", 
  "element_start", "element_end", "attributes", "attribute", "pi", 
  "cdata", "text", "doctype", 0
};
#endif

/* YYR1[YYN] -- Symbol number of symbol that rule YYN derives. */
static const short yyr1[] =
{
       0,    21,    21,    22,    22,    22,    22,    22,    22,    22,
      22,    23,    24,    24,    25,    25,    26,    27,    27,    28,
      28,    28,    28,    28,    28,    29,    29,    30,    31,    31,
      32
};

/* YYR2[YYN] -- Number of symbols composing right hand side of rule YYN. */
static const short yyr2[] =
{
       0,     1,     2,     1,     1,     1,     1,     1,     1,     1,
       1,     3,     1,     2,     4,     4,     3,     0,     2,     5,
       5,     4,     4,     3,     1,     4,     3,     3,     0,     2,
       3
};

/* YYDEFACT[S] -- default rule to reduce with in state S when YYTABLE
   doesn't specify something else to do.  Zero means the default is an
   error. */
static const short yydefact[] =
{
       0,     9,    10,     0,     0,     0,     0,    28,     0,     0,
       1,     5,     3,     4,     6,     7,     8,    12,     0,    17,
       0,     0,     0,     0,     2,    13,    11,    24,     0,    17,
      16,     0,    26,    29,    27,    30,     0,    14,    15,    18,
      25,    23,     0,     0,     0,    21,     0,    22,    19,    20,
       0,     0
};

static const short yydefgoto[] =
{
       9,    10,    11,    18,    12,    13,    28,    29,    14,    15,
      22,    16
};

static const short yypact[] =
{
      18,-32768,-32768,    -1,    -3,     4,     8,-32768,    21,     0,
  -32768,-32768,-32768,-32768,-32768,-32768,-32768,-32768,     3,    30,
      24,     9,    -2,    29,-32768,-32768,-32768,    17,     5,    30,
  -32768,    -6,-32768,-32768,-32768,-32768,    16,-32768,-32768,-32768,
  -32768,-32768,    26,    20,    28,-32768,    31,-32768,-32768,-32768,
      43,-32768
};

static const short yypgoto[] =
{
  -32768,    35,-32768,-32768,-32768,-32768,    19,-32768,-32768,-32768,
  -32768,-32768
};


#define	YYLAST		48


static const short yytable[] =
{
      50,    33,    17,     1,     2,     3,    25,     4,    19,    26,
       5,    40,    31,    37,    38,    20,     6,    34,     7,    21,
       8,     1,     2,     3,    23,     4,    32,    41,     5,    36,
      42,    43,    30,    46,     6,    47,     7,    35,     8,    44,
      45,    27,    48,    51,    24,     0,    49,     0,    39
};

static const short yycheck[] =
{
       0,     3,     3,     3,     4,     5,     3,     7,    11,     6,
      10,    17,     3,     8,     9,    11,    16,    19,    18,    11,
      20,     3,     4,     5,     3,     7,    17,    11,    10,    12,
      14,    15,     8,    13,    16,    15,    18,     8,    20,    13,
      14,    11,    14,     0,     9,    -1,    15,    -1,    29
};
#define YYPURE 1

/* -*-C-*-  Note some compilers choke on comments on `#line' lines.  */
#line 3 "/usr/share/bison/bison.simple"

/* Skeleton output parser for bison,

   Copyright (C) 1984, 1989, 1990, 2000, 2001, 2002 Free Software
   Foundation, Inc.

   This program is free software; you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation; either version 2, or (at your option)
   any later version.

   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with this program; if not, write to the Free Software
   Foundation, Inc., 59 Temple Place - Suite 330,
   Boston, MA 02111-1307, USA.  */

/* As a special exception, when this file is copied by Bison into a
   Bison output file, you may use that output file without restriction.
   This special exception was added by the Free Software Foundation
   in version 1.24 of Bison.  */

/* This is the parser code that is written into each bison parser when
   the %semantic_parser declaration is not specified in the grammar.
   It was written by Richard Stallman by simplifying the hairy parser
   used when %semantic_parser is specified.  */

/* All symbols defined below should begin with yy or YY, to avoid
   infringing on user name space.  This should be done even for local
   variables, as they might otherwise be expanded by user macros.
   There are some unavoidable exceptions within include files to
   define necessary library symbols; they are noted "INFRINGES ON
   USER NAME SPACE" below.  */

#if ! defined (yyoverflow) || defined (YYERROR_VERBOSE)

/* The parser invokes alloca or malloc; define the necessary symbols.  */

# if YYSTACK_USE_ALLOCA
#  define YYSTACK_ALLOC alloca
# else
#  ifndef YYSTACK_USE_ALLOCA
#   if defined (alloca) || defined (_ALLOCA_H)
#    define YYSTACK_ALLOC alloca
#   else
#    ifdef __GNUC__
#     define YYSTACK_ALLOC __builtin_alloca
#    endif
#   endif
#  endif
# endif

# ifdef YYSTACK_ALLOC
   /* Pacify GCC's `empty if-body' warning. */
#  define YYSTACK_FREE(Ptr) do { /* empty */; } while (0)
# else
#  if defined (__STDC__) || defined (__cplusplus)
#   include <stdlib.h> /* INFRINGES ON USER NAME SPACE */
#   define YYSIZE_T size_t
#  endif
#  define YYSTACK_ALLOC malloc
#  define YYSTACK_FREE free
# endif
#endif /* ! defined (yyoverflow) || defined (YYERROR_VERBOSE) */


#if (! defined (yyoverflow) \
     && (! defined (__cplusplus) \
	 || (YYLTYPE_IS_TRIVIAL && YYSTYPE_IS_TRIVIAL)))

/* A type that is properly aligned for any stack member.  */
union yyalloc
{
  short yyss;
  YYSTYPE yyvs;
# if YYLSP_NEEDED
  YYLTYPE yyls;
# endif
};

/* The size of the maximum gap between one aligned stack and the next.  */
# define YYSTACK_GAP_MAX (sizeof (union yyalloc) - 1)

/* The size of an array large to enough to hold all stacks, each with
   N elements.  */
# if YYLSP_NEEDED
#  define YYSTACK_BYTES(N) \
     ((N) * (sizeof (short) + sizeof (YYSTYPE) + sizeof (YYLTYPE))	\
      + 2 * YYSTACK_GAP_MAX)
# else
#  define YYSTACK_BYTES(N) \
     ((N) * (sizeof (short) + sizeof (YYSTYPE))				\
      + YYSTACK_GAP_MAX)
# endif

/* Copy COUNT objects from FROM to TO.  The source and destination do
   not overlap.  */
# ifndef YYCOPY
#  if 1 < __GNUC__
#   define YYCOPY(To, From, Count) \
      __builtin_memcpy (To, From, (Count) * sizeof (*(From)))
#  else
#   define YYCOPY(To, From, Count)		\
      do					\
	{					\
	  register YYSIZE_T yyi;		\
	  for (yyi = 0; yyi < (Count); yyi++)	\
	    (To)[yyi] = (From)[yyi];		\
	}					\
      while (0)
#  endif
# endif

/* Relocate STACK from its old location to the new one.  The
   local variables YYSIZE and YYSTACKSIZE give the old and new number of
   elements in the stack, and YYPTR gives the new location of the
   stack.  Advance YYPTR to a properly aligned location for the next
   stack.  */
# define YYSTACK_RELOCATE(Stack)					\
    do									\
      {									\
	YYSIZE_T yynewbytes;						\
	YYCOPY (&yyptr->Stack, Stack, yysize);				\
	Stack = &yyptr->Stack;						\
	yynewbytes = yystacksize * sizeof (*Stack) + YYSTACK_GAP_MAX;	\
	yyptr += yynewbytes / sizeof (*yyptr);				\
      }									\
    while (0)

#endif


#if ! defined (YYSIZE_T) && defined (__SIZE_TYPE__)
# define YYSIZE_T __SIZE_TYPE__
#endif
#if ! defined (YYSIZE_T) && defined (size_t)
# define YYSIZE_T size_t
#endif
#if ! defined (YYSIZE_T)
# if defined (__STDC__) || defined (__cplusplus)
#  include <stddef.h> /* INFRINGES ON USER NAME SPACE */
#  define YYSIZE_T size_t
# endif
#endif
#if ! defined (YYSIZE_T)
# define YYSIZE_T unsigned int
#endif

#define yyerrok		(yyerrstatus = 0)
#define yyclearin	(yychar = YYEMPTY)
#define YYEMPTY		-2
#define YYEOF		0
#define YYACCEPT	goto yyacceptlab
#define YYABORT 	goto yyabortlab
#define YYERROR		goto yyerrlab1
/* Like YYERROR except do call yyerror.  This remains here temporarily
   to ease the transition to the new meaning of YYERROR, for GCC.
   Once GCC version 2 has supplanted version 1, this can go.  */
#define YYFAIL		goto yyerrlab
#define YYRECOVERING()  (!!yyerrstatus)
#define YYBACKUP(Token, Value)					\
do								\
  if (yychar == YYEMPTY && yylen == 1)				\
    {								\
      yychar = (Token);						\
      yylval = (Value);						\
      yychar1 = YYTRANSLATE (yychar);				\
      YYPOPSTACK;						\
      goto yybackup;						\
    }								\
  else								\
    { 								\
      yyerror ("syntax error: cannot back up");			\
      YYERROR;							\
    }								\
while (0)

#define YYTERROR	1
#define YYERRCODE	256


/* YYLLOC_DEFAULT -- Compute the default location (before the actions
   are run).

   When YYLLOC_DEFAULT is run, CURRENT is set the location of the
   first token.  By default, to implement support for ranges, extend
   its range to the last symbol.  */

#ifndef YYLLOC_DEFAULT
# define YYLLOC_DEFAULT(Current, Rhs, N)       	\
   Current.last_line   = Rhs[N].last_line;	\
   Current.last_column = Rhs[N].last_column;
#endif


/* YYLEX -- calling `yylex' with the right arguments.  */

#if YYPURE
# if YYLSP_NEEDED
#  ifdef YYLEX_PARAM
#   define YYLEX		yylex (&yylval, &yylloc, YYLEX_PARAM)
#  else
#   define YYLEX		yylex (&yylval, &yylloc)
#  endif
# else /* !YYLSP_NEEDED */
#  ifdef YYLEX_PARAM
#   define YYLEX		yylex (&yylval, YYLEX_PARAM)
#  else
#   define YYLEX		yylex (&yylval)
#  endif
# endif /* !YYLSP_NEEDED */
#else /* !YYPURE */
# define YYLEX			yylex ()
#endif /* !YYPURE */


/* Enable debugging if requested.  */
#if YYDEBUG

# ifndef YYFPRINTF
#  include <stdio.h> /* INFRINGES ON USER NAME SPACE */
#  define YYFPRINTF fprintf
# endif

# define YYDPRINTF(Args)			\
do {						\
  if (yydebug)					\
    YYFPRINTF Args;				\
} while (0)
/* Nonzero means print parse trace.  It is left uninitialized so that
   multiple parsers can coexist.  */
int yydebug;
#else /* !YYDEBUG */
# define YYDPRINTF(Args)
#endif /* !YYDEBUG */

/* YYINITDEPTH -- initial size of the parser's stacks.  */
#ifndef	YYINITDEPTH
# define YYINITDEPTH 200
#endif

/* YYMAXDEPTH -- maximum size the stacks can grow to (effective only
   if the built-in stack extension method is used).

   Do not make this value too large; the results are undefined if
   SIZE_MAX < YYSTACK_BYTES (YYMAXDEPTH)
   evaluated with infinite-precision integer arithmetic.  */

#if YYMAXDEPTH == 0
# undef YYMAXDEPTH
#endif

#ifndef YYMAXDEPTH
# define YYMAXDEPTH 10000
#endif

#ifdef YYERROR_VERBOSE

# ifndef yystrlen
#  if defined (__GLIBC__) && defined (_STRING_H)
#   define yystrlen strlen
#  else
/* Return the length of YYSTR.  */
static YYSIZE_T
#   if defined (__STDC__) || defined (__cplusplus)
yystrlen (const char *yystr)
#   else
yystrlen (yystr)
     const char *yystr;
#   endif
{
  register const char *yys = yystr;

  while (*yys++ != '\0')
    continue;

  return yys - yystr - 1;
}
#  endif
# endif

# ifndef yystpcpy
#  if defined (__GLIBC__) && defined (_STRING_H) && defined (_GNU_SOURCE)
#   define yystpcpy stpcpy
#  else
/* Copy YYSRC to YYDEST, returning the address of the terminating '\0' in
   YYDEST.  */
static char *
#   if defined (__STDC__) || defined (__cplusplus)
yystpcpy (char *yydest, const char *yysrc)
#   else
yystpcpy (yydest, yysrc)
     char *yydest;
     const char *yysrc;
#   endif
{
  register char *yyd = yydest;
  register const char *yys = yysrc;

  while ((*yyd++ = *yys++) != '\0')
    continue;

  return yyd - 1;
}
#  endif
# endif
#endif

#line 315 "/usr/share/bison/bison.simple"


/* The user can define YYPARSE_PARAM as the name of an argument to be passed
   into yyparse.  The argument should have type void *.
   It should actually point to an object.
   Grammar actions can access the variable by casting it
   to the proper pointer type.  */

#ifdef YYPARSE_PARAM
# if defined (__STDC__) || defined (__cplusplus)
#  define YYPARSE_PARAM_ARG void *YYPARSE_PARAM
#  define YYPARSE_PARAM_DECL
# else
#  define YYPARSE_PARAM_ARG YYPARSE_PARAM
#  define YYPARSE_PARAM_DECL void *YYPARSE_PARAM;
# endif
#else /* !YYPARSE_PARAM */
# define YYPARSE_PARAM_ARG
# define YYPARSE_PARAM_DECL
#endif /* !YYPARSE_PARAM */

/* Prevent warning if -Wstrict-prototypes.  */
#ifdef __GNUC__
# ifdef YYPARSE_PARAM
int yyparse (void *);
# else
int yyparse (void);
# endif
#endif

/* YY_DECL_VARIABLES -- depending whether we use a pure parser,
   variables are global, or local to YYPARSE.  */

#define YY_DECL_NON_LSP_VARIABLES			\
/* The lookahead symbol.  */				\
int yychar;						\
							\
/* The semantic value of the lookahead symbol. */	\
YYSTYPE yylval;						\
							\
/* Number of parse errors so far.  */			\
int yynerrs;

#if YYLSP_NEEDED
# define YY_DECL_VARIABLES			\
YY_DECL_NON_LSP_VARIABLES			\
						\
/* Location data for the lookahead symbol.  */	\
YYLTYPE yylloc;
#else
# define YY_DECL_VARIABLES			\
YY_DECL_NON_LSP_VARIABLES
#endif


/* If nonreentrant, generate the variables here. */

#if !YYPURE
YY_DECL_VARIABLES
#endif  /* !YYPURE */

int
yyparse (YYPARSE_PARAM_ARG)
     YYPARSE_PARAM_DECL
{
  /* If reentrant, generate the variables here. */
#if YYPURE
  YY_DECL_VARIABLES
#endif  /* !YYPURE */

  register int yystate;
  register int yyn;
  int yyresult;
  /* Number of tokens to shift before error messages enabled.  */
  int yyerrstatus;
  /* Lookahead token as an internal (translated) token number.  */
  int yychar1 = 0;

  /* Three stacks and their tools:
     `yyss': related to states,
     `yyvs': related to semantic values,
     `yyls': related to locations.

     Refer to the stacks thru separate pointers, to allow yyoverflow
     to reallocate them elsewhere.  */

  /* The state stack. */
  short	yyssa[YYINITDEPTH];
  short *yyss = yyssa;
  register short *yyssp;

  /* The semantic value stack.  */
  YYSTYPE yyvsa[YYINITDEPTH];
  YYSTYPE *yyvs = yyvsa;
  register YYSTYPE *yyvsp;

#if YYLSP_NEEDED
  /* The location stack.  */
  YYLTYPE yylsa[YYINITDEPTH];
  YYLTYPE *yyls = yylsa;
  YYLTYPE *yylsp;
#endif

#if YYLSP_NEEDED
# define YYPOPSTACK   (yyvsp--, yyssp--, yylsp--)
#else
# define YYPOPSTACK   (yyvsp--, yyssp--)
#endif

  YYSIZE_T yystacksize = YYINITDEPTH;


  /* The variables used to return semantic value and location from the
     action routines.  */
  YYSTYPE yyval;
#if YYLSP_NEEDED
  YYLTYPE yyloc;
#endif

  /* When reducing, the number of symbols on the RHS of the reduced
     rule. */
  int yylen;

  YYDPRINTF ((stderr, "Starting parse\n"));

  yystate = 0;
  yyerrstatus = 0;
  yynerrs = 0;
  yychar = YYEMPTY;		/* Cause a token to be read.  */

  /* Initialize stack pointers.
     Waste one element of value and location stack
     so that they stay on the same level as the state stack.
     The wasted elements are never initialized.  */

  yyssp = yyss;
  yyvsp = yyvs;
#if YYLSP_NEEDED
  yylsp = yyls;
#endif
  goto yysetstate;

/*------------------------------------------------------------.
| yynewstate -- Push a new state, which is found in yystate.  |
`------------------------------------------------------------*/
 yynewstate:
  /* In all cases, when you get here, the value and location stacks
     have just been pushed. so pushing a state here evens the stacks.
     */
  yyssp++;

 yysetstate:
  *yyssp = yystate;

  if (yyssp >= yyss + yystacksize - 1)
    {
      /* Get the current used size of the three stacks, in elements.  */
      YYSIZE_T yysize = yyssp - yyss + 1;

#ifdef yyoverflow
      {
	/* Give user a chance to reallocate the stack. Use copies of
	   these so that the &'s don't force the real ones into
	   memory.  */
	YYSTYPE *yyvs1 = yyvs;
	short *yyss1 = yyss;

	/* Each stack pointer address is followed by the size of the
	   data in use in that stack, in bytes.  */
# if YYLSP_NEEDED
	YYLTYPE *yyls1 = yyls;
	/* This used to be a conditional around just the two extra args,
	   but that might be undefined if yyoverflow is a macro.  */
	yyoverflow ("parser stack overflow",
		    &yyss1, yysize * sizeof (*yyssp),
		    &yyvs1, yysize * sizeof (*yyvsp),
		    &yyls1, yysize * sizeof (*yylsp),
		    &yystacksize);
	yyls = yyls1;
# else
	yyoverflow ("parser stack overflow",
		    &yyss1, yysize * sizeof (*yyssp),
		    &yyvs1, yysize * sizeof (*yyvsp),
		    &yystacksize);
# endif
	yyss = yyss1;
	yyvs = yyvs1;
      }
#else /* no yyoverflow */
# ifndef YYSTACK_RELOCATE
      goto yyoverflowlab;
# else
      /* Extend the stack our own way.  */
      if (yystacksize >= YYMAXDEPTH)
	goto yyoverflowlab;
      yystacksize *= 2;
      if (yystacksize > YYMAXDEPTH)
	yystacksize = YYMAXDEPTH;

      {
	short *yyss1 = yyss;
	union yyalloc *yyptr =
	  (union yyalloc *) YYSTACK_ALLOC (YYSTACK_BYTES (yystacksize));
	if (! yyptr)
	  goto yyoverflowlab;
	YYSTACK_RELOCATE (yyss);
	YYSTACK_RELOCATE (yyvs);
# if YYLSP_NEEDED
	YYSTACK_RELOCATE (yyls);
# endif
# undef YYSTACK_RELOCATE
	if (yyss1 != yyssa)
	  YYSTACK_FREE (yyss1);
      }
# endif
#endif /* no yyoverflow */

      yyssp = yyss + yysize - 1;
      yyvsp = yyvs + yysize - 1;
#if YYLSP_NEEDED
      yylsp = yyls + yysize - 1;
#endif

      YYDPRINTF ((stderr, "Stack size increased to %lu\n",
		  (unsigned long int) yystacksize));

      if (yyssp >= yyss + yystacksize - 1)
	YYABORT;
    }

  YYDPRINTF ((stderr, "Entering state %d\n", yystate));

  goto yybackup;


/*-----------.
| yybackup.  |
`-----------*/
yybackup:

/* Do appropriate processing given the current state.  */
/* Read a lookahead token if we need one and don't already have one.  */
/* yyresume: */

  /* First try to decide what to do without reference to lookahead token.  */

  yyn = yypact[yystate];
  if (yyn == YYFLAG)
    goto yydefault;

  /* Not known => get a lookahead token if don't already have one.  */

  /* yychar is either YYEMPTY or YYEOF
     or a valid token in external form.  */

  if (yychar == YYEMPTY)
    {
      YYDPRINTF ((stderr, "Reading a token: "));
      yychar = YYLEX;
    }

  /* Convert token to internal form (in yychar1) for indexing tables with */

  if (yychar <= 0)		/* This means end of input. */
    {
      yychar1 = 0;
      yychar = YYEOF;		/* Don't call YYLEX any more */

      YYDPRINTF ((stderr, "Now at end of input.\n"));
    }
  else
    {
      yychar1 = YYTRANSLATE (yychar);

#if YYDEBUG
     /* We have to keep this `#if YYDEBUG', since we use variables
	which are defined only if `YYDEBUG' is set.  */
      if (yydebug)
	{
	  YYFPRINTF (stderr, "Next token is %d (%s",
		     yychar, yytname[yychar1]);
	  /* Give the individual parser a way to print the precise
	     meaning of a token, for further debugging info.  */
# ifdef YYPRINT
	  YYPRINT (stderr, yychar, yylval);
# endif
	  YYFPRINTF (stderr, ")\n");
	}
#endif
    }

  yyn += yychar1;
  if (yyn < 0 || yyn > YYLAST || yycheck[yyn] != yychar1)
    goto yydefault;

  yyn = yytable[yyn];

  /* yyn is what to do for this token type in this state.
     Negative => reduce, -yyn is rule number.
     Positive => shift, yyn is new state.
       New state is final state => don't bother to shift,
       just return success.
     0, or most negative number => error.  */

  if (yyn < 0)
    {
      if (yyn == YYFLAG)
	goto yyerrlab;
      yyn = -yyn;
      goto yyreduce;
    }
  else if (yyn == 0)
    goto yyerrlab;

  if (yyn == YYFINAL)
    YYACCEPT;

  /* Shift the lookahead token.  */
  YYDPRINTF ((stderr, "Shifting token %d (%s), ",
	      yychar, yytname[yychar1]));

  /* Discard the token being shifted unless it is eof.  */
  if (yychar != YYEOF)
    yychar = YYEMPTY;

  *++yyvsp = yylval;
#if YYLSP_NEEDED
  *++yylsp = yylloc;
#endif

  /* Count tokens shifted since error; after three, turn off error
     status.  */
  if (yyerrstatus)
    yyerrstatus--;

  yystate = yyn;
  goto yynewstate;


/*-----------------------------------------------------------.
| yydefault -- do the default action for the current state.  |
`-----------------------------------------------------------*/
yydefault:
  yyn = yydefact[yystate];
  if (yyn == 0)
    goto yyerrlab;
  goto yyreduce;


/*-----------------------------.
| yyreduce -- Do a reduction.  |
`-----------------------------*/
yyreduce:
  /* yyn is the number of a rule to reduce with.  */
  yylen = yyr2[yyn];

  /* If YYLEN is nonzero, implement the default value of the action:
     `$$ = $1'.

     Otherwise, the following line sets YYVAL to the semantic value of
     the lookahead token.  This behavior is undocumented and Bison
     users should not rely upon it.  Assigning to YYVAL
     unconditionally makes the parser a bit smaller, and it avoids a
     GCC warning that YYVAL may be used uninitialized.  */
  yyval = yyvsp[1-yylen];

#if YYLSP_NEEDED
  /* Similarly for the default location.  Let the user run additional
     commands if for instance locations are ranges.  */
  yyloc = yylsp[1-yylen];
  YYLLOC_DEFAULT (yyloc, (yylsp - yylen), yylen);
#endif

#if YYDEBUG
  /* We have to keep this `#if YYDEBUG', since we use variables which
     are defined only if `YYDEBUG' is set.  */
  if (yydebug)
    {
      int yyi;

      YYFPRINTF (stderr, "Reducing via rule %d (line %d), ",
		 yyn, yyrline[yyn]);

      /* Print the symbols being reduced, and their result.  */
      for (yyi = yyprhs[yyn]; yyrhs[yyi] > 0; yyi++)
	YYFPRINTF (stderr, "%s ", yytname[yyrhs[yyi]]);
      YYFPRINTF (stderr, " -> %s\n", yytname[yyr1[yyn]]);
    }
#endif

  switch (yyn) {

case 1:
#line 62 "htmlparse.y"
{;
    break;}
case 2:
#line 63 "htmlparse.y"
{;
    break;}
case 3:
#line 67 "htmlparse.y"
{;
    break;}
case 4:
#line 68 "htmlparse.y"
{;
    break;}
case 5:
#line 69 "htmlparse.y"
{;
    break;}
case 6:
#line 70 "htmlparse.y"
{;
    break;}
case 7:
#line 71 "htmlparse.y"
{;
    break;}
case 8:
#line 72 "htmlparse.y"
{;
    break;}
case 9:
#line 74 "htmlparse.y"
{
       UserData* ud = yyget_extra(scanner);
       PyObject* callback = NULL;
       PyObject* result = NULL;
       int error = 0;
       if (PyObject_HasAttrString(ud->handler, "characters")==1) {
	   callback = PyObject_GetAttrString(ud->handler, "characters");
	   if (callback==NULL) { error=1; goto finish_characters; }
	   result = PyObject_CallFunction(callback, "O", yyvsp[0]);
	   if (result==NULL) { error=1; goto finish_characters; }
       }
   finish_characters:
       Py_XDECREF(callback);
       Py_XDECREF(result);
       Py_DECREF(yyvsp[0]);
       if (error) {
	   PyErr_Fetch(&(ud->exc_type), &(ud->exc_val), &(ud->exc_tb));
	   YYABORT;
       }
   ;
    break;}
case 10:
#line 94 "htmlparse.y"
{;
    break;}
case 11:
#line 99 "htmlparse.y"
{
	UserData* ud = yyget_extra(scanner);
        PyObject* callback = NULL;
        PyObject* result = NULL;
        int error = 0;
        if (PyObject_HasAttrString(ud->handler, "comment")==1) {
            callback = PyObject_GetAttrString(ud->handler, "comment");
            if (callback==NULL) { error=1; goto finish_comment; }
            result = PyObject_CallFunction(callback, "O", yyvsp[-1]);
            if (result==NULL) { error=1; goto finish_comment; }
        }
    finish_comment:
        Py_XDECREF(callback);
        Py_XDECREF(result);
        Py_DECREF(yyvsp[-1]);
        if (error) {
            PyErr_Fetch(&(ud->exc_type), &(ud->exc_val), &(ud->exc_tb));
            YYABORT;
        }
    ;
    break;}
case 12:
#line 122 "htmlparse.y"
{ yyval = yyvsp[0]; ;
    break;}
case 13:
#line 124 "htmlparse.y"
{
        PyString_ConcatAndDel(&yyvsp[-1], yyvsp[0]);
        yyval = yyvsp[-1];
    ;
    break;}
case 14:
#line 132 "htmlparse.y"
{
        UserData* ud = yyget_extra(scanner);
        PyObject* callback = NULL;
        PyObject* result = NULL;
        int error = 0;
	PyObject* ltag = PyObject_CallMethod(yyvsp[-2], "lower", NULL);
        if (ltag==NULL) { error=1; goto finish_start1; }
        if (PyObject_HasAttrString(ud->handler, "startElement")==1) {
            callback = PyObject_GetAttrString(ud->handler, "startElement");
            if (callback==NULL) { error=1; goto finish_start1; }
            result = PyObject_CallFunction(callback, "OO", ltag, yyvsp[-1]);
            if (result==NULL) { error=1; goto finish_start1; }
        }
    finish_start1:
        Py_XDECREF(ltag);
        Py_XDECREF(callback);
        Py_XDECREF(result);
        Py_DECREF(yyvsp[-2]);
        Py_DECREF(yyvsp[-1]);
        if (error) {
            PyErr_Fetch(&(ud->exc_type), &(ud->exc_val), &(ud->exc_tb));
            YYABORT;
        }
    ;
    break;}
case 15:
#line 157 "htmlparse.y"
{
        UserData* ud = yyget_extra(scanner);
        PyObject* callback = NULL;
        PyObject* result = NULL;
        int error = 0;
        PyObject* ltag = PyObject_CallMethod(yyvsp[-2], "lower", NULL);
        if (ltag==NULL) { error=1; goto finish_start2; }
        if (PyObject_HasAttrString(ud->handler, "startElement")==1) {
            callback = PyObject_GetAttrString(ud->handler, "startElement");
            if (callback==NULL) { error=1; goto finish_start2; }
            result = PyObject_CallFunction(callback, "OO", ltag, yyvsp[-1]);
            if (result==NULL) { error=1; goto finish_start2; }
        }
        if (PyObject_HasAttrString(ud->handler, "endElement")==1) {
            callback = PyObject_GetAttrString(ud->handler, "endElement");
            if (callback==NULL) { error=1; goto finish_start2; }
            result = PyObject_CallFunction(callback, "O", ltag);
            if (result==NULL) { error=1; goto finish_start2; }
        }
    finish_start2:
        Py_XDECREF(ltag);
        Py_XDECREF(callback);
        Py_XDECREF(result);
        Py_DECREF(yyvsp[-2]);
        Py_DECREF(yyvsp[-1]);
        if (error) {
            PyErr_Fetch(&(ud->exc_type), &(ud->exc_val), &(ud->exc_tb));
            YYABORT;
        }
    ;
    break;}
case 16:
#line 191 "htmlparse.y"
{
        UserData* ud = yyget_extra(scanner);
        PyObject* callback = NULL;
        PyObject* result = NULL;
        int error = 0;
        PyObject* ltag = PyObject_CallMethod(yyvsp[-1], "lower", NULL);
        if (ltag==NULL) { error=1; goto finish_end; }
        if (PyObject_HasAttrString(ud->handler, "endElement")==1) {
            callback = PyObject_GetAttrString(ud->handler, "endElement");
            if (callback==NULL) { error=1; goto finish_end; }
            result = PyObject_CallFunction(callback, "O", ltag);
            if (result==NULL) { error=1; goto finish_end; }
        }
    finish_end:
        Py_XDECREF(ltag);
        Py_XDECREF(callback);
        Py_XDECREF(result);
        Py_DECREF(yyvsp[-1]);
        if (error) {
            PyErr_Fetch(&(ud->exc_type), &(ud->exc_val), &(ud->exc_tb));
            YYABORT;
        }
    ;
    break;}
case 17:
#line 218 "htmlparse.y"
{
        UserData* ud = yyget_extra(scanner);
        PyObject* dict = PyDict_New();
        if (dict==NULL) {
            PyErr_Fetch(&(ud->exc_type), &(ud->exc_val), &(ud->exc_tb));
            YYABORT;
        }
        yyval = dict;
    ;
    break;}
case 18:
#line 228 "htmlparse.y"
{
        UserData* ud = yyget_extra(scanner);
        PyObject* name = NULL;
        PyObject* val = NULL;
        int error = 0;
        name = PyTuple_GET_ITEM(yyvsp[-1], 0);
        if (name==NULL) { error = 1; goto finish_attributes; }
        val = PyTuple_GET_ITEM(yyvsp[-1], 1);
        if (val==NULL) { error = 1; goto finish_attributes; }
        if (PyDict_SetItem(yyvsp[0], name, val)==-1) { error = 1; goto finish_attributes; }
        yyval = yyvsp[0];
    finish_attributes:
        Py_DECREF(yyvsp[-1]);
	if (error) {
	    Py_XDECREF(name);
	    Py_XDECREF(val);
            Py_XDECREF(yyvsp[0]);
            PyErr_Fetch(&(ud->exc_type), &(ud->exc_val), &(ud->exc_tb));
            YYABORT;
        }
    ;
    break;}
case 19:
#line 257 "htmlparse.y"
{
        UserData* ud = yyget_extra(scanner);
	PyObject* lname = NULL;
        PyObject* val = NULL;
        PyObject* tup = NULL;
	int error = 0;
        lname = PyObject_CallMethod(yyvsp[-4], "lower", NULL);
	if (lname==NULL) { error = 1; goto finish_attr1; }
	val = quote_string(yyvsp[-2]);
	if (val==NULL) { error = 1; goto finish_attr1; }
        tup = Py_BuildValue("(OO)", lname, val);
        if (tup==NULL) { error = 1; goto finish_attr1; }
        yyval = tup;
    finish_attr1:
	Py_DECREF(yyvsp[-4]);
	if (val!=yyvsp[-2]) {
	    Py_DECREF(yyvsp[-2]);
	}
	if (error) {
            Py_XDECREF(tup);
	    Py_XDECREF(lname);
            Py_XDECREF(val);
            PyErr_Fetch(&(ud->exc_type), &(ud->exc_val), &(ud->exc_tb));
            YYABORT;
        }
    ;
    break;}
case 20:
#line 284 "htmlparse.y"
{
        UserData* ud = yyget_extra(scanner);
	PyObject* lname = NULL;
        PyObject* val = NULL;
        PyObject* tup = NULL;
	int error = 0;
        lname = PyObject_CallMethod(yyvsp[-4], "lower", NULL);
	if (lname==NULL) { error = 1; goto finish_attr1b; }
	val = quote_string(yyvsp[-2]);
	if (val==NULL) { error = 1; goto finish_attr1b; }
        tup = Py_BuildValue("(OO)", lname, val);
        if (tup==NULL) { error = 1; goto finish_attr1b; }
        yyval = tup;
    finish_attr1b:
        Py_DECREF(yyvsp[-4]);
	if (val!=yyvsp[-2]) {
	    Py_DECREF(yyvsp[-2]);
	}
	if (error) {
            Py_XDECREF(tup);
	    Py_XDECREF(lname);
            Py_XDECREF(val);
            PyErr_Fetch(&(ud->exc_type), &(ud->exc_val), &(ud->exc_tb));
            YYABORT;
        }
    ;
    break;}
case 21:
#line 311 "htmlparse.y"
{
        UserData* ud = yyget_extra(scanner);
	PyObject* lname = NULL;
        PyObject* val = NULL;
        PyObject* tup = NULL;
        int error = 0;
	lname = PyObject_CallMethod(yyvsp[-3], "lower", NULL);
	if (lname==NULL) { error = 1; goto finish_attr2; }
	val = PyString_FromString("''");
	if (val==NULL) { error = 1; goto finish_attr2; }
        tup = Py_BuildValue("(OO)", lname, val);
        if (tup==NULL) { error = 1; goto finish_attr2; }
        yyval = tup;
    finish_attr2:
        Py_DECREF(yyvsp[-3]);
	if (error) {
	    Py_XDECREF(lname);
	    Py_XDECREF(val);
	    Py_XDECREF(tup);
            PyErr_Fetch(&(ud->exc_type), &(ud->exc_val), &(ud->exc_tb));
            YYABORT;
        }
    ;
    break;}
case 22:
#line 335 "htmlparse.y"
{
        UserData* ud = yyget_extra(scanner);
	PyObject* lname = NULL;
        PyObject* val = NULL;
        PyObject* tup = NULL;
        int error = 0;
	lname = PyObject_CallMethod(yyvsp[-3], "lower", NULL);
	if (lname==NULL) { error = 1; goto finish_attr2b; }
	val = PyString_FromString("''");
	if (val==NULL) { error = 1; goto finish_attr2b; }
        tup = Py_BuildValue("(OO)", lname, val);
        if (tup==NULL) { error = 1; goto finish_attr2b; }
        yyval = tup;
    finish_attr2b:
        Py_DECREF(yyvsp[-3]);
	if (error) {
	    Py_XDECREF(lname);
	    Py_XDECREF(val);
	    Py_XDECREF(tup);
            PyErr_Fetch(&(ud->exc_type), &(ud->exc_val), &(ud->exc_tb));
            YYABORT;
        }
    ;
    break;}
case 23:
#line 359 "htmlparse.y"
{
        UserData* ud = yyget_extra(scanner);
        PyObject* lname = NULL;
        PyObject* tup = NULL;
        int error = 0;
        lname = PyObject_CallMethod(yyvsp[-2], "lower", NULL);
        if (lname==NULL) { error = 1; goto finish_attr3; }
        tup = Py_BuildValue("(OO)", lname, yyvsp[0]);
        if (tup==NULL) { error = 1; goto finish_attr3; }
        yyval = tup;
    finish_attr3:
        Py_DECREF(yyvsp[-2]);
	if (error) {
	    Py_XDECREF(lname);
            Py_XDECREF(tup);
            PyErr_Fetch(&(ud->exc_type), &(ud->exc_val), &(ud->exc_tb));
            YYABORT;
        }
    ;
    break;}
case 24:
#line 379 "htmlparse.y"
{
        UserData* ud = yyget_extra(scanner);
        PyObject* lname = NULL;
        PyObject* tup = NULL;
        int error = 0;
        lname = PyObject_CallMethod(yyvsp[0], "lower", NULL);
	if (lname==NULL) { error = 1; goto finish_attr4; }
        Py_INCREF(Py_None);
        tup = Py_BuildValue("(OO)", lname, Py_None);
        if (tup==NULL) { error = 1; goto finish_attr4; }
        yyval = tup;
    finish_attr4:
        Py_DECREF(yyvsp[0]);
	if (error) {
	    Py_XDECREF(lname);
            Py_XDECREF(tup);
            PyErr_Fetch(&(ud->exc_type), &(ud->exc_val), &(ud->exc_tb));
            YYABORT;
        }
    ;
    break;}
case 25:
#line 403 "htmlparse.y"
{
        UserData* ud = yyget_extra(scanner);
        PyObject* callback = NULL;
        PyObject* result = NULL;
        int error = 0;
        if (PyObject_HasAttrString(ud->handler, "pi")==1) {
            callback = PyObject_GetAttrString(ud->handler, "pi");
            if (callback==NULL) { error=1; goto finish_pi1; }
            result = PyObject_CallFunction(callback, "OO", yyvsp[-2], yyvsp[-1]);
            if (result==NULL) { error=1; goto finish_pi1; }
        }
    finish_pi1:
        Py_XDECREF(callback);
        Py_XDECREF(result);
        Py_DECREF(yyvsp[-2]);
        Py_DECREF(yyvsp[-1]);
        if (error) {
            PyErr_Fetch(&(ud->exc_type), &(ud->exc_val), &(ud->exc_tb));
            YYABORT;
        }
    ;
    break;}
case 26:
#line 425 "htmlparse.y"
{
        UserData* ud = yyget_extra(scanner);
        PyObject* callback = NULL;
        PyObject* result = NULL;
        int error = 0;
        if (PyObject_HasAttrString(ud->handler, "pi")==1) {
            callback = PyObject_GetAttrString(ud->handler, "pi");
            if (callback==NULL) { error=1; goto finish_pi2; }
            result = PyObject_CallFunction(callback, "O", yyvsp[-1]);
            if (result==NULL) { error=1; goto finish_pi2; }
        }
    finish_pi2:
        Py_XDECREF(callback);
        Py_XDECREF(result);
        Py_DECREF(yyvsp[-1]);
        if (error) {
            PyErr_Fetch(&(ud->exc_type), &(ud->exc_val), &(ud->exc_tb));
            YYABORT;
        }
    ;
    break;}
case 27:
#line 448 "htmlparse.y"
{
        UserData* ud = yyget_extra(scanner);
        PyObject* callback = NULL;
        PyObject* result = NULL;
        int error = 0;
        if (PyObject_HasAttrString(ud->handler, "cdata")==1) {
            callback = PyObject_GetAttrString(ud->handler, "cdata");
            if (callback==NULL) { error=1; goto finish_cdata; }
            result = PyObject_CallFunction(callback, "O", yyvsp[-1]);
            if (result==NULL) { error=1; goto finish_cdata; }
        }
    finish_cdata:
        Py_XDECREF(callback);
        Py_XDECREF(result);
        Py_DECREF(yyvsp[-1]);
        if (error) {
            PyErr_Fetch(&(ud->exc_type), &(ud->exc_val), &(ud->exc_tb));
            YYABORT;
        }
    ;
    break;}
case 28:
#line 471 "htmlparse.y"
{
        UserData* ud = yyget_extra(scanner);
        PyObject* result = PyString_FromString("");
        if (result==NULL) {
            PyErr_Fetch(&(ud->exc_type), &(ud->exc_val), &(ud->exc_tb));
            YYABORT;
        }
        yyval = result;
    ;
    break;}
case 29:
#line 481 "htmlparse.y"
{
        UserData* ud = yyget_extra(scanner);
        PyString_ConcatAndDel(&yyvsp[-1], yyvsp[0]);
        if (yyvsp[-1]==NULL) {
            PyErr_Fetch(&(ud->exc_type), &(ud->exc_val), &(ud->exc_tb));
            YYABORT;
        }
        yyval = yyvsp[-1];
    ;
    break;}
case 30:
#line 495 "htmlparse.y"
{
	UserData* ud = yyget_extra(scanner);
	PyObject* callback = NULL;
        PyObject* result = NULL;
        int error = 0;
        if (PyObject_HasAttrString(ud->handler, "doctype")==1) {
            callback = PyObject_GetAttrString(ud->handler, "doctype");
            if (callback==NULL) { error=1; goto finish_doctype; }
            result = PyObject_CallFunction(callback, "O", yyvsp[-1]);
            if (result==NULL) { error=1; goto finish_doctype; }
        }
    finish_doctype:
        Py_XDECREF(callback);
        Py_XDECREF(result);
        Py_DECREF(yyvsp[-1]);
        if (error) {
            PyErr_Fetch(&(ud->exc_type), &(ud->exc_val), &(ud->exc_tb));
            YYABORT;
        }
    ;
    break;}
}

#line 705 "/usr/share/bison/bison.simple"


  yyvsp -= yylen;
  yyssp -= yylen;
#if YYLSP_NEEDED
  yylsp -= yylen;
#endif

#if YYDEBUG
  if (yydebug)
    {
      short *yyssp1 = yyss - 1;
      YYFPRINTF (stderr, "state stack now");
      while (yyssp1 != yyssp)
	YYFPRINTF (stderr, " %d", *++yyssp1);
      YYFPRINTF (stderr, "\n");
    }
#endif

  *++yyvsp = yyval;
#if YYLSP_NEEDED
  *++yylsp = yyloc;
#endif

  /* Now `shift' the result of the reduction.  Determine what state
     that goes to, based on the state we popped back to and the rule
     number reduced by.  */

  yyn = yyr1[yyn];

  yystate = yypgoto[yyn - YYNTBASE] + *yyssp;
  if (yystate >= 0 && yystate <= YYLAST && yycheck[yystate] == *yyssp)
    yystate = yytable[yystate];
  else
    yystate = yydefgoto[yyn - YYNTBASE];

  goto yynewstate;


/*------------------------------------.
| yyerrlab -- here on detecting error |
`------------------------------------*/
yyerrlab:
  /* If not already recovering from an error, report this error.  */
  if (!yyerrstatus)
    {
      ++yynerrs;

#ifdef YYERROR_VERBOSE
      yyn = yypact[yystate];

      if (yyn > YYFLAG && yyn < YYLAST)
	{
	  YYSIZE_T yysize = 0;
	  char *yymsg;
	  int yyx, yycount;

	  yycount = 0;
	  /* Start YYX at -YYN if negative to avoid negative indexes in
	     YYCHECK.  */
	  for (yyx = yyn < 0 ? -yyn : 0;
	       yyx < (int) (sizeof (yytname) / sizeof (char *)); yyx++)
	    if (yycheck[yyx + yyn] == yyx)
	      yysize += yystrlen (yytname[yyx]) + 15, yycount++;
	  yysize += yystrlen ("parse error, unexpected ") + 1;
	  yysize += yystrlen (yytname[YYTRANSLATE (yychar)]);
	  yymsg = (char *) YYSTACK_ALLOC (yysize);
	  if (yymsg != 0)
	    {
	      char *yyp = yystpcpy (yymsg, "parse error, unexpected ");
	      yyp = yystpcpy (yyp, yytname[YYTRANSLATE (yychar)]);

	      if (yycount < 5)
		{
		  yycount = 0;
		  for (yyx = yyn < 0 ? -yyn : 0;
		       yyx < (int) (sizeof (yytname) / sizeof (char *));
		       yyx++)
		    if (yycheck[yyx + yyn] == yyx)
		      {
			const char *yyq = ! yycount ? ", expecting " : " or ";
			yyp = yystpcpy (yyp, yyq);
			yyp = yystpcpy (yyp, yytname[yyx]);
			yycount++;
		      }
		}
	      yyerror (yymsg);
	      YYSTACK_FREE (yymsg);
	    }
	  else
	    yyerror ("parse error; also virtual memory exhausted");
	}
      else
#endif /* defined (YYERROR_VERBOSE) */
	yyerror ("parse error");
    }
  goto yyerrlab1;


/*--------------------------------------------------.
| yyerrlab1 -- error raised explicitly by an action |
`--------------------------------------------------*/
yyerrlab1:
  if (yyerrstatus == 3)
    {
      /* If just tried and failed to reuse lookahead token after an
	 error, discard it.  */

      /* return failure if at end of input */
      if (yychar == YYEOF)
	YYABORT;
      YYDPRINTF ((stderr, "Discarding token %d (%s).\n",
		  yychar, yytname[yychar1]));
      yychar = YYEMPTY;
    }

  /* Else will try to reuse lookahead token after shifting the error
     token.  */

  yyerrstatus = 3;		/* Each real token shifted decrements this */

  goto yyerrhandle;


/*-------------------------------------------------------------------.
| yyerrdefault -- current state does not do anything special for the |
| error token.                                                       |
`-------------------------------------------------------------------*/
yyerrdefault:
#if 0
  /* This is wrong; only states that explicitly want error tokens
     should shift them.  */

  /* If its default is to accept any token, ok.  Otherwise pop it.  */
  yyn = yydefact[yystate];
  if (yyn)
    goto yydefault;
#endif


/*---------------------------------------------------------------.
| yyerrpop -- pop the current state because it cannot handle the |
| error token                                                    |
`---------------------------------------------------------------*/
yyerrpop:
  if (yyssp == yyss)
    YYABORT;
  yyvsp--;
  yystate = *--yyssp;
#if YYLSP_NEEDED
  yylsp--;
#endif

#if YYDEBUG
  if (yydebug)
    {
      short *yyssp1 = yyss - 1;
      YYFPRINTF (stderr, "Error: state stack now");
      while (yyssp1 != yyssp)
	YYFPRINTF (stderr, " %d", *++yyssp1);
      YYFPRINTF (stderr, "\n");
    }
#endif

/*--------------.
| yyerrhandle.  |
`--------------*/
yyerrhandle:
  yyn = yypact[yystate];
  if (yyn == YYFLAG)
    goto yyerrdefault;

  yyn += YYTERROR;
  if (yyn < 0 || yyn > YYLAST || yycheck[yyn] != YYTERROR)
    goto yyerrdefault;

  yyn = yytable[yyn];
  if (yyn < 0)
    {
      if (yyn == YYFLAG)
	goto yyerrpop;
      yyn = -yyn;
      goto yyreduce;
    }
  else if (yyn == 0)
    goto yyerrpop;

  if (yyn == YYFINAL)
    YYACCEPT;

  YYDPRINTF ((stderr, "Shifting error token, "));

  *++yyvsp = yylval;
#if YYLSP_NEEDED
  *++yylsp = yylloc;
#endif

  yystate = yyn;
  goto yynewstate;


/*-------------------------------------.
| yyacceptlab -- YYACCEPT comes here.  |
`-------------------------------------*/
yyacceptlab:
  yyresult = 0;
  goto yyreturn;

/*-----------------------------------.
| yyabortlab -- YYABORT comes here.  |
`-----------------------------------*/
yyabortlab:
  yyresult = 1;
  goto yyreturn;

/*---------------------------------------------.
| yyoverflowab -- parser overflow comes here.  |
`---------------------------------------------*/
yyoverflowlab:
  yyerror ("parser stack overflow");
  yyresult = 2;
  /* Fall through.  */

yyreturn:
#ifndef yyoverflow
  if (yyss != yyssa)
    YYSTACK_FREE (yyss);
#endif
  return yyresult;
}
#line 517 "htmlparse.y"


/* create parser */
static PyObject* htmlsax_parser(PyObject* self, PyObject* args) {
    PyObject* handler;
    parser_object* p;
    if (!PyArg_ParseTuple(args, "O", &handler)) {
	PyErr_SetString(PyExc_TypeError, "SAX2 handler object arg required");
	return NULL;
    }

    if (!(p=PyObject_NEW(parser_object, &parser_type))) {
	PyErr_SetString(PyExc_TypeError, "Allocating parser object failed");
	return NULL;
    }
    p->userData = PyMem_New(UserData, sizeof(UserData));
    p->userData->handler = handler;
    p->userData->exc_type = NULL;
    p->userData->exc_val = NULL;
    p->userData->exc_tb = NULL;
    p->scanner = NULL;
    htmllexInit(&(p->scanner), p->userData);
    return (PyObject*) p;
}


static void parser_dealloc(parser_object* self)
{
    PyMem_Del(self->userData);
    PyMem_DEL(self);
}


static PyObject* parser_flush(parser_object* self, PyObject* args) {
    /* flush parser buffers */
    int res=0, error;
    if (!PyArg_ParseTuple(args, "")) {
	PyErr_SetString(PyExc_TypeError, "no args required");
        return NULL;
    }
    htmllexStop(self->scanner);
    self->userData->exc_type = NULL;
    self->userData->exc_val = NULL;
    self->userData->exc_tb = NULL;
    error = 0;
    if (error!=0) {
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


/* feed a chunk of data to the parser */
static PyObject* parser_feed(parser_object* self, PyObject* args) {
    /* set up the parse string */
    int slen;
    char* s;
    if (!PyArg_ParseTuple(args, "t#", &s, &slen)) {
	PyErr_SetString(PyExc_TypeError, "string arg required");
	return NULL;
    }

    /* reset error state */
    self->userData->exc_type = NULL;
    self->userData->exc_val = NULL;
    self->userData->exc_tb = NULL;
    
    /* parse */
    htmllexStart(self->scanner, s, slen);
    if (yyparse(self->scanner)!=0) {
        if (self->userData->exc_type!=NULL) {
	    /* note: we give away these objects, so dont decref */
            PyErr_Restore(self->userData->exc_type,
        		  self->userData->exc_val,
        		  self->userData->exc_tb);
        }
        return NULL;
    }
    Py_INCREF(Py_None);
    return Py_None;
}


static PyObject* parser_reset(parser_object* self, PyObject* args) {
    if (!PyArg_ParseTuple(args, "")) {
	PyErr_SetString(PyExc_TypeError, "no args required");
	return NULL;
    }
    htmllexStop(self->scanner);
    self->userData->exc_type = NULL;
    self->userData->exc_val = NULL;
    self->userData->exc_tb = NULL;
    self->scanner = NULL;
    htmllexInit(&(self->scanner), self->userData);
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
    //yydebug = 1;
}

int yyerror (char* msg) {
    fprintf(stderr, "htmllex: error: %s\n", msg);
    return 0;
}

/* Find out if and how we must quote the value as an HTML attribute.
 - quote if it contains white space or <>
 - quote with " if it contains '
 - quote with ' if it contains "

 val is a Python String object
*/
PyObject* quote_string (PyObject* val) {
    char* quote = NULL;
    int len = PyString_GET_SIZE(val);
    char* internal = PyString_AS_STRING(val);
    int i;
    PyObject* prefix;
    for (i=0; i<len; i++) {
	if (isspace(internal[i]) && !quote) {
            quote = "\"";
	}
	else if (internal[i]=='\'') {
	    quote = "\"";
            break;
	}
	else if (internal[i]=='"') {
	    quote = "'";
            break;
	}
    }
    if (quote==NULL) {
        return val;
    }
    // quote suffix
    if ((prefix = PyString_FromString(quote))==NULL) return NULL;
    PyString_Concat(&val, prefix);
    if (val==NULL) {
        Py_DECREF(prefix);
	return NULL;
    }
    // quote prefix
    PyString_ConcatAndDel(&prefix, val);
    if (prefix==NULL) {
        Py_DECREF(val);
	return NULL;
    }
    return prefix;
}
