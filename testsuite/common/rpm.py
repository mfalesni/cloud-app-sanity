#!/usr/bin/env python2
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

import shell
import rpm

import pytest

import os
import re

def keys_import(keydir="/etc/pki/rpm-gpg"):
    """ This function imports all keys in directory '/etc/pki/rpm-gpg' by default
    """
    file_list = os.listdir(keydir)
    for key_file in file_list:
        shell.run("rpm --import %s/%s" % (keydir, key_file))

def signature_lines(package):
    """ Returns lines with signature informations of package

    :param package: Package name
    :type package: ``str``

    :returns: List of lines speaking about signatures
    :rtype: ``list(str)``
    """
    sig = re.compile("[Ss]ignature")
    for line in shell.run("rpm -qvv %s" % package).strip().split("\n"):
        if sig.search(line):
            yield line.split("#", 1)[-1].lstrip()

def verify_package(package):
    """ Verifies package in RPM database.

    :param package: Package to check
    :type package: ``str``
    :returns: Bool whether verification succeeded
    :rtype: ``bool``
    """
    success = True
    for line in rpm.signature_lines(package):
        fields = [x.strip() for x in line.rsplit(", key ID", 1)]
        key_status = None
        if re.match("^[0-9a-z]+$", fields[1]):
            # RHEL 5
            key_status = fields[0]
        else:
            # RHEL 6
            key_status = fields[1]
        key_status = key_status.rsplit(":", 1)[1].strip()   # The key info is on the right side of the colon
        print "sig: %s -> %s" % (package, key_status)
        if not key_status.upper() == "OK":
            success = False
    return success

def package_problems(package):
    """ This functions returns reported problems with package

    :param package: Package to check
    :type package: ``str``
    :returns: ``STDOUT`` of rpm -V
    :rtype: ``str``
    """
    return shell.run("rpm -Vvv %s" % package, None)

def package_build_host(package):
    """ Returns build host of the package.

    :param package: Package to check
    :type package: ``str``
    :returns: Build host of the package
    :rtype: ``str``
    """
    return shell.run("rpm -q --qf \"%%{BUILDHOST}\" %s" % package).strip()

def package_installed(package):
    """ Returns whether is package installed or not

    :param package: Package name
    :type package: ``str``

    :returns: ``True`` when package is installed, otherwise ``False``
    :rtype: ``bool``
    """
    try:
        shell.run("rpm -q %s" % package)
        return True
    except AssertionError:
        return False

def q(package, qf=None):
    """ Performs a 'rpm -q' command with optional --qf parameter

    :param package: Package to query
    :type package: ``str``
    :param qf: ``--qf`` parameter value
    :type qf: ``str``

    :returns: Package informations
    :rtype: ``str``
    """
    cmd = "rpm -q "
    if qf != None:
        cmd += "--qf \"%s\" " % qf
    cmd += package
    return shell.run(cmd)

def qa(qf=None):
    """ Performs a 'rpm -qa' command with optional --qf parameter

    :param qf: ``--qf`` parameter value
    :type qf: ``str``

    :returns: Package informations
    :rtype: ``str``
    """
    cmd = "rpm -qa"
    if qf != None:
        cmd += " --qf \"%s\"" % qf
    return shell.run(cmd)