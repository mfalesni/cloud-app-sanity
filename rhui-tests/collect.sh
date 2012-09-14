#!/usr/bin/env bash

. ./lib.sh

[ ! -e "results" ] && {
  echo "Can't find file 'results'"
  exit 1
}

for f in `cat results` ;
do
  echo -ne "=> $f\n"
  cat $f
  echo ""
done
