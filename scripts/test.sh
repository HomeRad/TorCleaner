#!/bin/sh -e
P=`dirname $0`
RESOURCES=`$P/resources.sh`
$P/run.sh test.py $RESOURCES --coverage -pvcw "$@"
