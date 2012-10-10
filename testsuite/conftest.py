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

""" This module contains generator functions for variable injecting of py.test framework.
    
    Some of them are cached, some not. I don't know how to make multi-level dependency yet.
"""

import os
import re
import subprocess
import common

from ConfigParser import ConfigParser

def pytest_funcarg__audreyvars(request):
    """Setups variables for testing

    :param request: py.test request

    :returns: All Audrey-relevant environment variables.
    :rtype: dict
    """
    result = {}
    for key in os.environ:
        if key.startswith("AUDREY_VAR_KATELLO_REGISTER_"):
            result[re.sub("^AUDREY_VAR_KATELLO_REGISTER_", "", key)] = os.environ[key]

    return result


def pytest_funcarg__katello_discoverable(request):
    """Returns boolean (True of False) to indicate whether the provided katello
    server is accessible

    :param request: py.test.request

    :returns: Accesibility of Katello server
    :rtype: ``bool``

    """
    cmd = "ping -q -c5 %s" % request.getfuncargvalue("audreyvars")["KATELLO_HOST"]
    print "# %s" % cmd
    return subprocess.call(cmd.split()) == 0

def pytest_funcarg__tunnel_requested(request):
    """Determines whether setting up SSH tunnel is requested

    :param request: py.test request.

    :returns: Whether was tunnel requested.
    :rtype: ``bool``
    """
    audreyvars = request.getfuncargvalue("audreyvars")
    ec2_deployment = request.getfuncargvalue("ec2_deployment")
    ssh = audreyvars.get("SSH_TUNNEL_ENABLED", "Auto")

    # Did we ask for a tunnel to be setup
    if ssh.lower() == "true":
        return True

    # Or if we are 'auto' and running in ec2
    if ssh.lower() == "auto" and ec2_deployment:
        return True

    # Otherwise, it wasn't requested
    return False

def pytest_funcarg__ec2_deployment(request):
    """Setups cached variable whether it's ec2 deployment or not.

    :param request: py.test request.

    :returns: Whether is this EC2 deployment (cached).
    :rtype: ``bool``
    
    """
    return request.cached_setup(setup=setup_ec2_deployment, scope="module")

def setup_ec2_deployment():
    """Returns boolean True of False to indicate whether the current system is
       an ec2 image

    :returns: Whether is this EC2 deployment.
    :rtype: ``bool``
    """
    cmd = 'curl --silent http://169.254.169.254/latest/dynamic/instance-identity/document'
    print "# %s" % cmd
    return subprocess.call(cmd.split()) == 0

def pytest_funcarg__subscription_manager_version(request):
    """Setups cached variable of version of sub-man

    :param request: py.test request.

    :returns: SM version from cache
    :rtype: 2-tuple
    """
    return request.cached_setup(setup=setup_subscription_manager_version, scope="module")

def setup_subscription_manager_version():
    """Gets version of sub-man

    :returns: SM version
    :rtype: 2-tuple
    """
    sm_rpm_ver = common.shell.run("rpm -q --queryformat %{VERSION} subscription-manager")
    sm_ver_maj, sm_ver_min, sm_ver_rest = sm_rpm_ver.split(".", 2)
    return int(sm_ver_maj), int(sm_ver_min)

def pytest_funcarg__system_uuid(request):
    """ Returns system UUID from subscription-manager

    :param request: py.test request
    :returns: System UUID
    :rtype: ``str``
    """
    facts = common.shell.run("subscription-manager facts --list")
    facts = facts.strip().split("\n")
    for fact in facts:
        name, value = fact.split(":", 1)
        if name == "system.uuid":
            return value.lstrip()

def pytest_funcarg__selinux_enabled(request):
    """ Detects whether is SElinux enabled or not

    :param request: py.test request
    :returns: SElinux status
    :rtype: ``bool``
    """
    result = True
    try:
        common.shell.run("selinuxenabled")
    except AssertionError:
        result = False
    return result

def pytest_funcarg__selinux_getenforce(request):
    """ Returns current enforcing mode of SELinux

    :param request: py.test request
    :returns: SElinux enforcing status
    :rtype: ``str``
    """
    return common.shell.run("/usr/sbin/getenforce").strip()

def pytest_funcarg__selinux_getenforce_conf(request):
    """ Returns current enforcing mode of SELinux from config file

    :param request: py.test request
    :returns: SElinux enforcing status
    :rtype: ``str``
    """
    f = open("/etc/sysconfig/selinux", "r")
    lines = []
    for line in f.readlines():
        if line.startswith("SELINUX="):
            lines.append(line)
    f.close()
    # Check whether is only one
    assert len(lines) == 1
    return lines[0].split("=")[1].strip()

def pytest_funcarg__selinux_type(request):
    """ Returns current SELINUX type from config file

    :param request: py.test request
    :returns: SElinux type
    :rtype: ``str``
    """
    f = open("/etc/sysconfig/selinux", "r")
    lines = []
    for line in f.readlines():
        if line.startswith("SELINUXTYPE="):
            lines.append(line)
    f.close()
    # Check whether is only one
    assert len(lines) == 1
    return lines[0].split("=")[1].strip()

def pytest_funcarg__rpm_package_list(request):
    """ Returns list of all installed packages in computer.

    :param request: py.test request
    :returns: List of all installed packages in computer.
    :rtype: ``list``
    """
    raw = common.shell.run("rpm -qa").strip()
    return [x.strip() for x in raw.split("\n")]

def pytest_funcarg__rpm_package_list_names(request):
    """ Returns list of all installed packages in computer.

    :param request: py.test request
    :returns: List of all installed packages in computer.
    :rtype: ``list``
    """
    raw = common.shell.run("rpm -qa --qf \"%{NAME} \"").strip()
    return raw.split(" ")

def pytest_funcarg__rhel_release(request):
    """Returns RHEL version

    :returns: RHEL version
    :rtype: ``tuple``
    """
    redhat_release_content = common.shell.run("cat /etc/redhat-release").strip()
    redhat_version_field = redhat_release_content.split(" ")[6]
    return tuple(redhat_version_field.split(".", 1))

def pytest_funcarg__PATH(request):
    """ PATH environment variable

    :returns: List of directories in $PATH
    :rtype: ``list``
    """
    return os.environ["PATH"].split(":")

def pytest_funcarg__gpgcheck_enabled(request):
    """ Whether is GPG check enabled in yum

    :returns: GPG check status
    :rtype: ``bool``
    """
    config = ConfigParser()
    cfg.read(["/etc/yum.conf"])
    return int(cfg.get("main", "gpgcheck")) == 1

def pytest_funcarg__chkconfig_list(request):
    """ Returns list of all services with enablement in each runlevel

    :returns: All services.
    :rtype: ``dict``
    """
    result = {}
    stdout = common.shell.run("chkconfig --list").strip()
    for line in stdout.split("\n"):
        line = re.sub("[[:blank:]]+", "\t", line)
        fields = line.split("\t")
        servicename = fields[0].strip()
        fields = fields[1:]
        result[servicename] = {}
        for field in fields:
            (runlevel, status) = field.split(":")
            runlevel = int(runlevel)
            if status.lower() == "on":
                status = True
            elif status.lower() == "off":
                status = False
            else:
                pytest.fail(msg="Bad parsing of chkconfig --list")
            result[servicename][runlevel] = status
    return result
