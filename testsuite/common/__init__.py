#!/usr/bin/env python2
#   Author(s): Milan Falesnik <mfalesni@redhat.com>
#              James Laska <jlaska@redhat.com>
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

""" This module contains some functions, which are likely to be shared
    between modules.

    When decide to put a function here?:

        - When it's enough universal to be used with multiple modules
        - It can't be parameter for py.test
"""

from string import Template
import subprocess
import shlex
import re
from ConfigParser import ConfigParser
import os
import pytest
import shutil
import base64
from urllib2 import urlopen, URLError, HTTPError, Request
try:
    import json
except ImportError:
    import simplejson as json

class DownloadException(Exception):
    pass

audrey_service_path = '/var/audrey/tooling/user'
"""
:var audrey_service_path: Where are all Audrey services from XML located
"""

def run(cmd, errorcode=0):
    """This function runs desired command and checks whether it has failed or not

    :param cmd: Command to be run
    :type cmd: str or list (``shlex``-splitted)
    :param errorcode: Desired error code of the program. Defaults to 0 (all ok). If set to ``None``, error code won't be checked.
    :type errorcode: int
    
    :returns: ``STDOUT`` of called process
    :rtype: str
    :raises: AssertionError
    """
    print "# %s" % cmd
    if isinstance(cmd, str):
        cmd = shlex.split(cmd)
    p_open = subprocess.Popen(cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT)
    (stdout, stderr) = p_open.communicate()
    if errorcode != None:
        assert p_open.returncode == errorcode
    return stdout

def shellcall(command):
    """ Function used for calling shell commands rather than invoking programs.

    :param command: Command to be launched
    :type command: ``str``
    
    :returns: ``tuple`` of ``STDOUT`` and RC of the command
    :raises: AssertionError
    """
    process = subprocess.Popen(command,stdout=subprocess.PIPE, shell=True)
    (stdout, stderr) = process.communicate()
    return (stdout, process.returncode)

    
def copy(source, destination):
    if not os.path.isfile(source):
        pytest.fail(msg="Couldn't find file '%s'" % source)
    shutil.copy(source, destination)

def mkdir(directory):
    os.mkdir(directory)

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

def update_yum_config(repo_file, enabled=True):
    """Enables or disables all sections in Yum config files

    :param repo_file: Config file, which should be processed
    :type repo_file: str
    :param enabled: Whether to enable or disable
    :type enabled: bool

    """
    if os.path.isfile(repo_file):
        cfg = ConfigParser()
        cfg.read([repo_file])
        save_changes = False
        for section in cfg.sections():
            if cfg.has_option(section, 'enabled'):
                save_changes = True
                if enabled:
                    cfg.set(section, 'enabled', 1)
                else:
                    cfg.set(section, 'enabled', 0)
        if save_changes:
            fd = open(repo_file, 'rwa+')
            cfg.write(fd)
            fd.close()
    else:
        pytest.fail(msg="%s was not found!" % repo_file)

def update_yum_repo(repo_file, enabled=True):
    """Enables or disables all sections in Yum repository files

    :param repo_file: Repo file, which should be processed
    :type repo_file: str
    :param enabled: Whether to enable or disable
    :type enabled: bool
    """
    if not repo_file.startswith('/'):
        repo_file = '/etc/yum.repos.d/%s' % repo_file
    if not repo_file.endswith('.repo'):
        repo_file = '%s.repo' % repo_file
    update_yum_config(repo_file, enabled)

def update_yum_plugin(plugin_conf, enabled=True):
    """Enables or disables all sections in Yum plugin config files

    :param repo_file: Config file, which should be processed
    :type repo_file: str
    :param enabled: Whether to enable or disable
    :type enabled: bool
    """
    if not plugin_conf.startswith('/'):
        plugin_conf = '/etc/yum/pluginconf.d/%s' % plugin_conf
    if not plugin_conf.endswith('.conf'):
        plugin_conf = '%s.conf' % plugin_conf
    update_yum_config(plugin_conf, enabled)

def exists_in_path(file, actual_directory):
    """ This function looks whether a file exists in system PATH or actual directory.

    :param file: File to look for
    :type file: ``str``
    :param actual_directory: Actual directory we are in
    :type actual_directory: ``str``
    :returns: File existence ``True`` or ``False``
    :rtype: ``bool``
    """
    extensions = os.environ.get("PATHEXT", "").split(os.pathsep)
    pathdirs = os.environ.get("PATH", "").split(os.pathsep)
    pathdirs.append(actual_directory)
    for directory in pathdirs:
        base = os.path.join(directory, file)
        options = [base] + [(base + ext) for ext in extensions]
        for filename in options:
            if os.path.exists(filename):
                return True
    return False

def netstat_service_bound_localhost(service):
    """ This function checks whether certain service is bound only to localhost.

    :param service: Service name
    :type service: ``str``
    :returns: ``True`` when it's bound only to localhost, otherwise ``False``
    :rtype: ``bool``
    """
    netstat = run("netstat -t --listen")
    protocols = ["tcp", "udp"]
    local_addrs = ["127.0.0.1", "::1", "localhost"]
    for line in netstat.strip().split("\n"):
        fields = re.sub(" +", "\t", line).strip().split("\t")
        if fields[0] in protocols and fields[3].split(":")[-1] == service:
            address = fields[3].split(":")[0]
            if address not in local_addrs:
                print line
                pytest.fail(msg="Service '%s' listens to address %s!" % (service, address) )

def list_opened_files(pid):
    """ This function lists opened files of certain process specified by PID

    :param pid: PID of the process
    :type pid: ``int``
    """
    stdout = run("lsof -i 4 -a -p %d" % pid, None)
    lines = stdout.strip().split("\n")[1:]  # Ignore first line
    lines = [re.sub("\([^(]*\)$", "", line).rstrip() for line in lines]    # Ignore last parenthesis
    lines = [re.sub(" +", "\t", line).split("\t") for line in lines]    # Split into fields
    result = []
    for line in lines:
        result.append(line[-1])
    return result

def selinux_setenforce(mode):
    """ Sets enforcing mode of SElinux

    :param mode: Enforcing mode from [Permissive, Enforcing]
    :param type: ``str``
    :raises: pytest.Failed, AssertionError
    """
    assert mode in ["Permissive", "Enforcing"]
    run("/usr/sbin/setenforce %s" % mode)

def beaker_list_tests(inputfile):
    """Returns Beaker tasks list

    :returns: Beaker tasks list
    :rtype: ``list``
    """
    try:
        result, rc = shellcall("cd beaker-tests && ./list.sh %s" % inputfile)
        assert rc == 0
        return result.strip().split("\n")
    except AssertionError:
        pytest.fail(msg="Error when gathering list of Beaker tasks")