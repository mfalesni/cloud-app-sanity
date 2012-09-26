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
import base64
from urllib2 import urlopen, HTTPError, URLError, Request

class DownloadException(Exception):
    pass

def service_bound_localhost(service):
    """ This function checks whether certain service is bound only to localhost.

    :param service: Service name
    :type service: ``str``
    :returns: ``True`` when it's bound only to localhost, otherwise ``False``
    :rtype: ``bool``
    """
    netstat = shell.run("netstat -t --listen")
    protocols = ["tcp", "udp"]
    local_addrs = ["127.0.0.1", "::1", "localhost"]
    for line in netstat.strip().split("\n"):
        fields = re.sub(" +", "\t", line).strip().split("\t")
        if fields[0] in protocols and fields[3].split(":")[-1] == service:
            address = fields[3].split(":")[0]
            if address not in local_addrs:
                print line
                pytest.fail(msg="Service '%s' listens to address %s!" % (service, address) )

def download_file(url, target_file_name, bulletproof=False):
    """ Downloads file from desired URL. Can be specified as bulletproof,
        if downloading from Gitweb-site

    :param url: URL where to download from
    :type url: str
    :param target_file_name: Target file name
    :type target_file_name: str
    :param bulletproof: Whether it has to check if it didn't download garbage or not
    :type bulletproof: bool
    """
    trials = 10
    forbidden = "<!DOCTYPE html"
    result = None
    while result == None and trials > 0:
        try:
            try:
                handle = urlopen(url)
                content = handle.readlines()
                handle.close()
                if bulletproof:
                    for line in content:
                        if forbidden in line:
                            raise DownloadException("Wrong file format!")
                result = "\n".join(content)
            except (URLError, HTTPError, DownloadException):
                raise
        except (DownloadException, HTTPError, URLError):
            trials -= 1
            if trials == 0:
                raise
            continue
    try:
        target_file = open(target_file_name, "w")
        target_file.write(result)
        target_file.close()
    except TypeError:
        pytest.fail(msg="Download unsuccessful")

def make_auth_request(url, login, password):
    """ Creates request with basic HTTP authentication

    :param url: URL to use for request
    :type url: str
    :param login: Login name
    :type login: str
    :param password: Login password
    :type password: str
    :return: Basic HTTP authenticated request
    :rtype: urllib2.Request
    """
    request = Request(url)
    request.add_header("Authorization", "Basic %s" % base64.encodestring('%s:%s' % (login, password))[:-1])
    return request

def list_opened_files(pid):
    """ This function lists opened files of certain process specified by PID

    :param pid: PID of the process
    :type pid: ``int``
    """
    stdout = shell.run("lsof -i 4 -a -p %d" % pid, None)
    lines = stdout.strip().split("\n")[1:]  # Ignore first line
    lines = [re.sub("\([^(]*\)$", "", line).rstrip() for line in lines]    # Ignore last parenthesis
    lines = [re.sub(" +", "\t", line).split("\t") for line in lines]    # Split into fields
    result = []
    for line in lines:
        result.append(line[-1])
    return result