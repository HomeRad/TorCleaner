#ifndef BISON_HTMLPARSE_H
# define BISON_HTMLPARSE_H

# ifndef YYSTYPE
#  define YYSTYPE int
#  define YYSTYPE_IS_TRIVIAL 1
# endif
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


#endif /* not BISON_HTMLPARSE_H */
