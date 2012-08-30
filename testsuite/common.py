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

def append_file(target, fromf):
    """ This function appends one file to another

    :param target: Target file
    :type target: str
    :param target: Source file
    :type target: str

    :returns: None
    :rtype: None
    """    
    destination = open(target, "a")
    source = open(fromf, "r")
    destination.write(source.read())
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

def install_yum_package_local(package_name):
    """ Does the 'yum install <package>' command.

    :param package_name: Name of the package to install (eg. katello-all)
    :type package_name: str

    :raises: AssertionError
    """
    # Install it
    run("yum -y install %s" % (package_name))
    # Verify it
    run("rpm -q %s" % (package_name))

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

def install_yum_package_remote(server, uuid, login, password, package):
    """ This function installs package into guest system via Katello request.
        Basically, it tells Katello "Hey, Katello, install these packages into machine with that UUID"

    :param server: Remote Katello server
    :type server: ``str``
    :param uuid: Target machine UUID
    :type uuid: ``str``
    :param login: Login name into Katello server
    :type login: ``str``
    :param password: Login password into Katello server
    :type password: ``str``
    :param package: Package to install into system
    :type package: ``str``

    :raises: pytest.Failed    
    """
    # Prepare the request
    request = make_auth_request("https://%s/katello/api/systems/%s/packages" % (server, uuid), login, password)
    request.add_header("content-type", "application/json")
    body = json.dumps({"packages": [package]})
    request.add_header("content-length", str(len(body)))
    request.add_data(body)
    # send the request
    response = None
    try:
        response = urlopen(request)
    except HTTPError, e:
        if int(e.code) in [202]:
            response = e # To work in RHEL5
        else:
            pytest.fail(msg="Error when querying installation of package %s with HTTP code %d and reason '%s'!" % (package, int(e.code), e.reason))
    # get the task uuid
    task_uuid = json.loads("\n".join(response.readlines()))["uuid"]
    # poll it
    state = ""
    # List of allowed states
    ok_states = ["waiting", "running", "finished"]
    while state != "finished":
        state = katello_poll_system_task_state(server, task_uuid, login, password)
        if state not in ok_states:
            pytest.fail(msg="Installation of package %s failed when task went to state '%s'" % (str(package), state))
    # Package is installed, let's verify it
    run("rpm -q %s" % package)

def katello_poll_system_task_state(server, task_uuid, login, password):
    """ This function returns state of task with given UUID.
        Useful when polling certain task if finished or not.

    :param server: Katello server to poll on.
    :type server: ``str``
    :param task_uuid: Checked task's unique ID
    :type task_uuid: ``str``
    :param password: Login password into Katello server
    :type password: ``str``
    :param package: Package to install into system
    :type package: ``str``

    :returns: Reported task state
    :rtype: ``str``
    """
    request = make_auth_request("https://%s/katello/api/systems/tasks/%s" % (server, task_uuid), login, password)
    response = urlopen(request)
    data = json.loads("\n".join(response.readlines()))
    return str(data["state"])

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
                pytest.fail(msg="Service '%s' listens to address %s!" % (service, address) )
