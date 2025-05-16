#!/bin/bash

yarn run clean
yarn run build
yarn run compress
python setup.py bdist_wheel