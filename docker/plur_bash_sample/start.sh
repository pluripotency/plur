#! /bin/sh
CURRENT=$(cd $(dirname $0);pwd)
source $CURRENT/env
sh ${CURRENT}/build.sh

if docker ps -a | grep -q ${CONTAINER_NAME}; then
  docker rm -f `docker ps -aq -f name=^${CONTAINER_NAME}$`
fi

LOG_PARAMS=normal_on_tmp

docker run -it \
    --rm \
    --name ${IMAGE_NAME} \
    --net host \
    -e LOG_PARAMS=${LOG_PARAMS} \
    -v /tmp:/tmp:rw \
    ${IMAGE_NAME} .venv/bin/python main.py

