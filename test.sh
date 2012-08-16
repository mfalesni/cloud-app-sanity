#!/usr/bin/env bash

. "./settings.cfg"

[ ! -d "./python" ] && {
	echo "No environment prepared! Try using make bootstrap"
	exit 1
}

. "${PYDIR}/bin/activate"

cd testsuite

mkdir -p "${LOGDIR}"

"../${PYDIR}/bin/py.test" --junitxml="${LOGDIR}/${JUNITXML}" "${@}"
