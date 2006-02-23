#!/bin/sh
# Generate the Makefiles and configure files
if !( aclocal --version ) </dev/null > /dev/null 2>&1; then
    echo "aclocal not found -- aborting"
    exit
fi

if !( autoheader --version ) </dev/null > /dev/null 2>&1; then
    echo "autoheader not found -- aborting"
    exit
fi

if !( automake --version ) </dev/null > /dev/null 2>&1; then
    echo "automake not found -- aborting"
    exit
fi

if !( libtoolize --version ) </dev/null > /dev/null 2>&1; then
    echo "libtoolize not found -- aborting"
    exit
fi

if !( autoconf --version ) </dev/null > /dev/null 2>&1; then
    echo "autoconf not found -- aborting"
    exit
fi
echo "Building ltmain" && libtoolize --copy --force --automake && \
echo "Building macros" && aclocal && \
echo "Building config header template" && autoheader && \
echo "Building Makefiles" && automake --add-missing --gnu --copy && \
echo "Building configure" && autoconf
RES=$?
if [ $RES != 0 ]; then
    echo "Autogeneration failed (exit code $RES)"
    exit $RES
fi
echo 'run "./configure && make localbuild"'
