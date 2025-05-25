#! /bin/bash
CURRENT=$(cd $(dirname $0);pwd)

#ENV_NAME=v3
#VIRTUALENV_PATH=$HOME/.virtualenv/${ENV_NAME}
#PYTHON=${VIRTUALENV_PATH}/bin/python
PYTHON=python

$PYTHON -m unittest discover ${CURRENT} -v