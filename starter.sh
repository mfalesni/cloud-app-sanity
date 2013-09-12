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
            echo ">> Package ${PROGRAM} not found. Asking yum ..."
            PKG="`yum whatprovides --rpmverbosity=name ${PROGRAM} 2>/dev/null| grep -vE '^$' | grep -vE '^(Repo|Matched|Other)' | grep -E `uname -i` | sed -r -e 's/^([^:]+):.*?$/\1/' | sort -r | head -n1`"
            [ ! -z "${PKG}" ] && {
                yum install -y ${PKG} && {
                    echo ">> Package ${PKG} providing ${PROGRAM} successfully installed"
                } || {
                    echo ">> Package which would provide ${PROGRAM} not found"
                    exit 3
                }
            }
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
[ ! -d "./build" ] && ./virtualenv.py build
. build/bin/activate
pip install -Ur requirements.txt
py.test "${@}"