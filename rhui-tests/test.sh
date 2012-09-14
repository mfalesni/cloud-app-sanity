#!/usr/bin/env bash

# Source library
. ./lib.sh

[ -z "${1}" ] && {
  echo "Correct usage: $0 testname"
  exit 1
}

use lotr x # We are using LOTR executable

echo "`date`: Running test ${1}"
LOGFILE="`./lotr -r -y -v "${1}" | grep \"^LOGFILE: \" | sed -r -e \"s/^LOGFILE: //\"`"
echo "Parsing log file $LOGFILE"
cat $LOGFILE >&2
FAILED="`cat $LOGFILE | grep \"FAIL\"`"
SUCCESS="`echo $FAILED | wc -l`"
if [ $SUCCESS -ne 0 ] ; then
  echo "FAILED: ${1} !"
  exit 1
else
  echo "SUCCESS: ${1} !"
  exit 0
fi


