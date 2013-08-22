#!/usr/bin/env bash

[ -d cloud-app-sanity ] || git clone https://github.com/mfalesni/cloud-app-sanity.git 
cd cloud-app-sanity
git pull
mkdir -p results
rm -rf ./results/*
python setup.py test
