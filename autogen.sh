#!/bin/sh
# Generate the Makefiles and configure files
if !( autoreconf --version ) </dev/null > /dev/null 2>&1; then
    echo "autoreconf not found -- aborting"
    exit
fi

echo "Updating generated configuration files with autoreconf..." && autoreconf --force --install --verbose
RES=$?
if [ $RES != 0 ]; then
    echo "Autogeneration failed (exit code $RES)"
    exit $RES
fi
rm -rf autom4te*.cache
echo 'run "./configure && make localbuild"'
