#!/bin/bash -xe

python3 --version
py.test --version
python3 -mpep8 --version

# Target directory for all build files
BUILD=${1:-ci-build}
mkdir -p $BUILD

python3 -mpep8 --ignore E501 *.py tests/*.py

# Check that the setup.py script works
rm -rf ${BUILD}/test-install ${BUILD}/test-install-bin
mkdir ${BUILD}/test-install ${BUILD}/test-install-bin
PYTHONPATH=${BUILD}/test-install python3 setup.py --quiet install --install-lib ${BUILD}/test-install --install-scripts ${BUILD}/test-install-bin

# Unit tests
PYTHONPATH=${BUILD}/test-install py.test --junitxml ${BUILD}/testlog.xml tests

