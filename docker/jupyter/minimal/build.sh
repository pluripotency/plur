#! /bin/sh
CURRENT=$(cd $(dirname $0);pwd)
. $CURRENT/env
docker build -f $CURRENT/Dockerfile -t $IMAGE_NAME $CURRENT/../../..
