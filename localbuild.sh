#!/bin/sh
# install webcleaner in the current dir (for development)
./configure 2>&1 | tee localbuild.log
make localbuild 2>&1 | tee --append localbuild.log
