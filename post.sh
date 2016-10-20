#!/bin/bash
#
# $1 == json file to post
# $2 == URL to post

curl -X POST -d @$1 $2 \
    --header "Content-Type:application/json"