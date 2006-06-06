#!/bin/sh
#--http1.0
env http_proxy="http://localhost:8081" curl --request HEAD -v "$1"
