#!/usr/bin/env bash

cd cloud-app-sanity
git pull
mkdir -p results
rm -rf ./results/*
python setup.py test
