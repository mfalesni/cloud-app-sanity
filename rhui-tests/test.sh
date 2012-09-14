#!/usr/bin/env bash

# Source library
. ./lib.sh

[ -z "${1}" ] && {
  echo "Correct usage: $0 testname"
  exit 1
}

use lotr x # We are using LOTR executable

# Prepare results file
touch results

echo "`date`: Running test ${1}"
./lotr -r -y -v "${1}" | grep "^LOGFILE: " | sed -r -e "s/^LOGFILE: //" >> results
LOGFILE="`tail -n1 results`"
echo "Parsing log file $LOGFILE"
FAILED="`cat $LOGFILE | grep \"FAIL\"`"
SUCCESS="`echo $FAILED | wc -l`"
if [ $SUCCESS != "0" ] ; then
  echo "FAILED: ${1} !"
  exit 1
else
  echo "SUCCESS: ${1} !"
  exit 0
fi


