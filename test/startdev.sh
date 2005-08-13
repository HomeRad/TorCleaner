#!/bin/sh
CONFIG=${1:-localconfig}
test/run.sh webcleaner --config=$CONFIG --no-file-logs
