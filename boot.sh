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

# Display error and exit
error() {
    echo "$@"
    exit 1
}

# Display usage and exit
usage() {
    echo "$0 <options> [package(s)...]

Where <options> include:
   -b <build-dir>       Where to prepare build/test environment
"
    exit 1
}

# Parse command-line arguments
parse_args() {
    while getopts "d:h" options "$@" ; do
        case $options in
            d )     PYDIR=$OPTARG ;;
            \?|h )  usage ;;
            * )     usage ;;
        esac
    done

    # Any remaining arguments are used as PYPACKAGES
    PYPACKAGES=${@:$OPTIND}
    unset OPTIND

    # Error handling
    test -z "$PYDIR" && error "Missing -d <build-dir> arguement"
    test -z "$PYPACKAGES" && error "No python packages specified"
}

#
# Let's do something ...
#

PYDIR=""       # build directory location
PYPACKAGES=""  # What python packages to install into environment?

# Parse command-line arguments
parse_args "$@"

# Prepare environment
python bootstrap.py "${PYDIR}"

if [ $? -ne 0 ] ; then
    echo "Error preparing bootstrap '${PYDIR}'"
    exit 1
fi

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
