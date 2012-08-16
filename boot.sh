#!/usr/bin/env bash

# Load test suite settings
. "./settings.cfg"

# Prepare environment
python bootstrap.py "${PYDIR}"

# Activating environment
echo "----- Activating environment -----"
. "${PYDIR}/bin/activate"

# Install things you need
echo "----- Installing desired packages -----"
for package in $PYPACKAGES
do
	echo "Installing ${package}"
	"${PYDIR}/bin/easy_install" "${package}" >/dev/null 2>&1
	ec=$?
	( [ $ec -ne 0 ] && {
		echo "    Installation failed!"
		exit $ec
	} ) || echo "    Package installed correctly!"
done
echo "----- Packages installed -----"

# Delete unneeded files
echo "----- Cleaning up -----"

#for f in bootstrap.py
#do
#	echo "Deleting file ${f}"
#	rm -f "${f}"
#done



echo "----- DONE! -----"