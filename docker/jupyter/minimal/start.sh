#! /bin/sh
CURRENT=$(cd $(dirname $0);pwd)
. $CURRENT/env

sh ${CURRENT}/build.sh
if docker ps -a | grep -q ${IMAGE_NAME}; then
  docker rm -f `docker ps -aq -f name=^${IMAGE_NAME}$`
fi

docker run \
    --rm \
    --name ${CONTAINER_NAME} \
    -it \
    --net host \
    -v /tmp:/tmp:rw \
    ${IMAGE_NAME}

