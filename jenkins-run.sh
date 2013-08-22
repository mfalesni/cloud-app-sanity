#!/usr/bin/env bash

git pull
mkdir -p results
rm -rf ./results/*
python setup.py test
