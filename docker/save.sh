#! /bin/sh
CURRENT=$(cd $(dirname $0);pwd)
source $CURRENT/env
SAVE_DIR=$CURRENT/..

if [ -d ${SAVE_DIR} ]; then
  sh ${CURRENT}/build.sh

  echo Saving ${IMAGE_NAME} image
  docker save -o ${IMAGE_NAME}.tar ${IMAGE_NAME}
  echo Compressing ${IMAGE_NAME} image
  gzip ${IMAGE_NAME}.tar
  echo Archiving ${IMAGE_NAME} image
  mv ${IMAGE_NAME}.tar.gz ${SAVE_DIR}
fi
