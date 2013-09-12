#!/usr/bin/env bash

# CAS suite starter and requirements checker

. ./starter-settings

function ensure_installed_rpm()
{
    RPM="${1}"
    rpm -q "${1}" > /dev/null 2>&1 && {
        echo ">> Package ${RPM} already installed."
    } || {
        echo ">> Package ${RPM} is not installed, installing ..."
        yum install -y "${RPM}" && {
            echo ">> Package successfully installed"
        } || {
            echo ">> Failed to install ${RPM} package. Quitting"
            exit 2
        }
    }
}

function ensure_installed_program()
{
    PROGRAM="${1}"
    hash "${PROGRAM}" && {
        echo ">> Program ${PROGRAM} already installed"
    } || {
        echo ">> Program ${PROGRAM} is not installed. Trying yum install ${PROGRAM}"
        yum install -y "${PROGRAM}" && {
            echo ">> Program ${PROGRAM} successfully installed via yum"
        } || {
            echo ">> Installation of program ${PROGRAM} via yum failed. Quitting"
            exit 3
        }
    }
}

echo "cloud-app-sanity testing suite starter script"
echo "> Checking required software to be present"
for program in $REQUIRED_PROGRAMS
do
    ensure_installed_program $program
done

for package in $REQUIRED_YUM_PACKAGES
do
    ensure_installed_rpm $package
done
echo "Command-line parameters: ${@}"
./virtualenv.py build
. build/bin/activate
py.test "${@}"