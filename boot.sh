#!/usr/bin/env bash
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#   Description:	CloudForms CloudForms Applications Sanity Test Suite
#					bootstrap file.
#   Author(s): Milan Falesnik <mfalesni@redhat.com>
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#   Copyright (c) 2012 Red Hat, Inc. All rights reserved.
#
#   This copyrighted material is made available to anyone wishing
#   to use, modify, copy, or redistribute it subject to the terms
#   and conditions of the GNU General Public License version 2.
#
#   This program is distributed in the hope that it will be
#   useful, but WITHOUT ANY WARRANTY; without even the implied
#   warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#   PURPOSE. See the GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public
#   License along with this program; if not, write to the Free
#   Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
#   Boston, MA 02110-1301, USA.
#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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