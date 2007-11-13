#!/bin/sh
CONFIG=${1:-localconfig}
if [ "$CONFIG" = "localconfig" ]; then
    export WC_DEVELOPMENT=1
fi
`dirname $0`/run.sh webcleaner --config=$CONFIG --no-file-logs
