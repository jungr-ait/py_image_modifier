#! /bin/bash
################################################################################
#
# Copyright (C) 2022 Roland Jung
# All rights reserved.
#
################################################################################

CUR_DIR=${PWD}
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
VENV_DIR=${DIR}/python-venv


# create virtual environment
if [ ! -d "$VENV_DIR" ]; then
  mkdir ${VENV_DIR} 
fi  

cd ${VENV_DIR}

# install dependencies:
sudo apt install libheif-examples
sudo apt-get install python3-venv


python3 -m pip install virtualenv
python3 -m pip install --upgrade pip
python3 -m venv env
source env/bin/activate
which python

# install requirements:
pip install -r ${DIR}/requirements.txt


pip install --upgrade --force-reinstall Pillow

cd ${CUR_DIR}


