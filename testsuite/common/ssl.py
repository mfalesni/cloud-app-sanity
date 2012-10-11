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

import pytest

import re


def openssl_config():
    """ Returns content of the /etc/pki/tls/openssl.cnf file

    :returns: Contents of the config file
    :rtype: ``str``
    """
    config = open("/etc/pki/tls/openssl.cnf", "r")
    contents = config.read().strip()
    config.close()
    return contents

def openssl_config_strip(data):
    """ removes comments and blank lines from the loaded config file

    :param data: Data to strip
    :type data: ``str``

    :returns: Content without comments and blank lines
    :rtype: ``str``
    """
    result = []
    for line in data.split("\n"):
        work_line = line.strip()
        work_line = re.sub("([^#]*)#.*?$", "\\1", work_line)
        if len(work_line) > 0:
            result.append(work_line)
    return "\n".join(result)

def openssl_config_get_section(section):
    """ Gets section from OpenSSL config file

    :param section: Section name
    :type section: ``str``

    :returns: Dict of keys->values in section
    :rtype: ``dict``
    """
    result = {}
    parses = False
    for line in openssl_config_strip(openssl_config()).split("\n"):
        if line.lstrip().startswith("[") and line.rstrip().endswith("]") and line[1:-1].strip() == section:
            parses = True
            continue
        if parses:
            if line.strip().startswith("["):
                break
            (key, value) = line.strip().split("=", 1)
            result[key.strip()] = value.strip()
    return result