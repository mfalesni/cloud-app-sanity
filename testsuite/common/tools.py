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

from string import Template
import re
import pytest

def filename_from_url(url):
    """ Extracts the filename from given URL

    :param url: URL to be used for extraction
    :type url: str

    :returns: File name from URL
    :rtype: str
    """
    while url.endswith("/"):
        url = url[:-1] # Strip the trailing /
    return re.sub("^.*?/([^/]+)$", r"\1", url)

def append_file(target, fromf, strip_sep=False):
    """ This function appends one file to another.
        It's possible to strip the content from blank characters at beginning and end + separate the contents by \n

    :param target: Target file
    :type target: str
    :param target: Source file
    :type target: str
    :param strip_sep: Whether to strip the contents and separate new file by \n
    :type strip_sep: ``bool``

    :returns: None
    :rtype: None
    """    
    destination = open(target, "a")
    source = open(fromf, "r")
    data = source.read()
    if strip_sep:
        data = "%s\n" % data.strip()
    destination.write(data)
    source.close()
    destination.close()

def s_format(s, dct):
    """ Does the ``dict``-format of string.
        Python-version-proof.

    :param s: Formatting string
    :type s: str

    :param dct: Replacing dictionary
    :type dct: dict

    :returns: Formatted string.
    :rtype: str

    """
    if hasattr(s, 'format'):
        return s.format(**dct)
    else:
        # convert python-2.6 format to something 2.4 can handle
        return Template(re.sub(r'{([^}]+)}', '$\\1', s)).substitute(dct)

def service_active_in_runlevels(chkconfig_list, service, runlevels=(3,5)):
    """ Does the check of service presence in desired runlevels

    :param chkconfig_list: ``dict`` from ``pytest_funcarg__chkconfig_list`` - list of all chkconfig services details injected by py.test
    :type chkconfig_list: ``dict``

    :param service: Service name
    :type service: ``str``

    :param runlevels: Tuple, list or any kind of iterable that yields integers of desired runlevels
    :type runlevels: Iterable (``tuple``, ``list``)

    :returns: Whether is the service active in all specified runlevels
    :rtype: ``bool``

    :raises: ``KeyError``
    """
    for runlevel in runlevels:
        if not chkconfig_list[service][runlevel]:
            return False

    return True