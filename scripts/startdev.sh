#!/bin/sh
CONFIG=${1:-localconfig}
DIR=`dirname $0`
$DIR/run.sh webcleaner --config=$CONFIG --no-file-logs
