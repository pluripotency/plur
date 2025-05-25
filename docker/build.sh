#! /bin/sh
CURRENT=$(cd $(dirname $0);pwd)
source $CURRENT/env
docker build -f ${CURRENT}/plur_uv/Dockerfile -t ${IMAGE_NAME} ${CURRENT}/..
