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

import os
import re
import pytest
import common.shell
import common.rpm

class RPMPackageFailure(Exception):
    pass

class RPMScriptletFailure(Exception):
    pass

RPM_PROBLEMS_MESSAGES = {   "S": "size",
                            "M": "mode",
                            "5": "MD5 checksum",
                            "D": "major and minor numbers",
                            "L": "symbolic link contents",
                            "U": "owner",
                            "G": "group",
                            "T": "modification time"}

def check_for_errors(text):
    """ This function checks for errors in text and returns text unchanged

    :param text: text to be checked
    :type text: ``str``

    :returns: text
    :rtype: ``str``
    """
    errors = {'failure in rpm package': RPMPackageFailure, 'scriptlet failed, exit status 1': RPMScriptletFailure}
    for error in errors.keys():
        if error in text:
            raise errors.keys()[error](text)
    return text

def keys_import(keydir="/etc/pki/rpm-gpg"):
    """ This function imports all keys in directory '/etc/pki/rpm-gpg' by default
    """
    file_list = os.listdir(keydir)
    for key_file in file_list:
        common.shell.run("rpm --import %s/%s" % (keydir, key_file))

def signature_lines(package_lines):
    """ Returns lines with signature informations of package

    :param package_lines: rpm --verify output for the package
    :type package_lines: ``list[str]``

    :returns: List of lines speaking about signatures
    :rtype: ``list(str)``
    """
    sig = re.compile("[Ss]ignature")
    for line in package_lines:
        if sig.search(line):
            yield line.split("#", 1)[-1].lstrip()

def wrong_files_lines(package_lines):
    """ Returns lines with problem files

    :param package_lines: rpm --verify output for the package
    :type package_lines: ``list[str]``

    :returns: List of lines speaking about wrong something about files
    :rtype: ``list(str)``
    """
    for line in package_lines:
        line = line.strip()
        if not line.startswith(".........") and len(line) > 0:
            yield line

def verify_package_files(package):
    """ Verifies package in RPM database.

        Checks output of the rpm -Vvv and looks for files, which have some problems (see http://www.rpm.org/max-rpm/s1-rpm-verify-output.html)

    :param package: Package to check
    :type package: ``str``
    :returns: Bool whether verification succeeded
    :rtype: ``bool``
    """
    problems = []
    source, stderr, rc = common.shell.command_stderr("rpm -Vvv %s" % package)
    source = source.strip().split("\n")
    if int(rc) != 0:
        problems.append("RPM $?=%d" % int(rc))
    for line in common.rpm.wrong_files_lines(source):
        status_type, filename = line.split("/", 1)
        filename = "/" + filename
        status_type = re.sub(r"\s+", " ", status_type).strip().split()
        status = status_type[0]
        file_type = ""
        if len(status_type) > 1:
            file_type = status_type[1].strip()
        # if file_type == "c":
        #     continue
        status_problems = []
        for key in RPM_PROBLEMS_MESSAGES:
            if key in status:
                status_problems.append(RPM_PROBLEMS_MESSAGES[key])
        if len(status_problems) == 0:
            status_problems.append(status)
            #TODO config?

        problems.append("file %s has problems with %s" % (filename, ", ".join(status_problems) ) )
    return problems

def verify_package_signed(package):
    """ Verifies package in RPM database.

        Checks for signature.

    :param package: Package to check
    :type package: ``str``
    :returns: Bool whether verification of signature succeeded
    :rtype: ``bool``
    """
    problems = []
    stdout, stderr, rc = common.shell.command_stderr("rpm -qvv %s" % package)
    stderr = stderr.strip().split("\n")
    if int(rc) != 0:
        problems.append("RPM $?=%d" % int(rc))
    for line in common.rpm.signature_lines(stderr):
        fields = [x.strip() for x in line.rsplit(", key ID", 1)]
        key_status = None
        if re.match("^[0-9a-z]+$", fields[1]):
            # RHEL 5
            key_status = fields[0]
        else:
            # RHEL 6
            key_status = fields[1]
        key_status = key_status.rsplit(":", 1)[1].strip()   # The key info is on the right side of the colon
        if not key_status.upper() == "OK":
            problems.append("No key signature")
    return problems

def package_problems(package):
    """ This functions returns reported problems with package

    :param package: Package to check
    :type package: ``str``
    :returns: ``STDOUT`` of rpm -V
    :rtype: ``str``
    """
    return common.shell.run("rpm -Vvv %s" % package, None)

def package_build_host(package):
    """ Returns build host of the package.

    :param package: Package to check
    :type package: ``str``
    :returns: Build host of the package
    :rtype: ``str``
    """
    return common.shell.run("rpm -q --qf \"%%{BUILDHOST}\" %s" % package).strip()

def package_installed(package):
    """ Returns whether is package installed or not

    :param package: Package name
    :type package: ``str``

    :returns: ``True`` when package is installed, otherwise ``False``
    :rtype: ``bool``
    """
    try:
        common.shell.run("rpm -q %s" % package)
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
    return common.shell.run(cmd)

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
    return common.shell.run(cmd)

def e(package):
    """ Performs a 'rpm -e' command

    :param package: Package to be removed
    :type package: ``str``
    """
    return common.shell.run("rpm -e %s" % package)

def ql(package):
    """ Performs a 'rpm -ql' command

    :param package: Package to be listed
    :type package: ``str``
    """
    return common.shell.run("rpm -ql %s" % package)
