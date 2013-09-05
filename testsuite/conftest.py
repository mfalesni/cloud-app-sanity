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
    Update 2013-08-19: Cahnged to newer styled fixtures. Dependency now should work O.K. :)
"""

import pytest
import os
import re
import subprocess

# This loads the PluginProxy, no need to write this inside tests
import plugins

#Deprecated
import common.services

from ConfigParser import ConfigParser

try:
    import json
except ImportError:
    import simplejson as json

@pytest.fixture
def audreyvars():
    """Setups variables for testing

    :returns: All Audrey-relevant environment variables.
    :rtype: dict
    """
    result = {}
    for key in os.environ:
        if key.startswith("AUDREY_VAR_KATELLO_REGISTER_"):
            result[re.sub("^AUDREY_VAR_KATELLO_REGISTER_", "", key)] = os.environ[key]

    return result

@pytest.fixture
def katello_discoverable(request):
    """Returns boolean (True of False) to indicate whether the provided katello
    server is accessible

    :param request: py.test.request

    :returns: Accesibility of Katello server
    :rtype: ``bool``

    """
    cmd = "ping -q -c5 %s" % request.getfuncargvalue("audreyvars")["KATELLO_HOST"]
    print "# %s" % cmd
    return subprocess.call(cmd.split()) == 0

@pytest.fixture
def tunnel_requested(request):
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

@pytest.fixture
def system_groups():
    """Determine applicable system groups for the current system

    :returns: All Audrey-relevant environment variables.
    :rtype: dict
    """
    group_names = []

    # A group for the current system platform (aka $basearch)
    group_names.append(Test.Yum.get_yum_variable('basearch'))

    # A group for the current system release (aka $releasever)
    # Per katello rules, replace any non-alpha-numeric character with a '_'
    group_names.append(re.sub(r'\W', '_', Test.Yum.get_yum_variable('releasever')))

    # A group to indicate which provider the instance is deployed to
    if is_rhev_deployment():
        group_names.append('provider_rhev')
    if is_vsphere_deployment():
        group_names.append('provider_vsphere')
    if ec2_deployment():
        group_names.append('provider_ec2')
        # Add a group name for the ec2 region
        result = Test.Run.command('curl --fail http://169.254.169.254/latest/dynamic/instance-identity/document')
        buf, rc = result.stdout, result.rc
        if rc == 0:
            ec2_data = json.loads(buf)
            if ec2_data.has_key('region'):
                group_names.append('ec2-%s' % ec2_data.get('region'))

    return group_names

@pytest.fixture(scope="session")
def is_rhev_deployment():
    """Setups cached variable whether it's RHEV deployment or not.

    :returns: Whether is this RHEV deployment (cached).
    :rtype: ``bool``

    """
    try:
        Test.RPM.query('rhev-agent')
        return True
    except AssertionError:
        pass

    try:
        assert Test.Run.bash("grep -qi rhev /sys/class/virtio-ports/*/name")
        return True
    except AssertionError:
        pass

    return False

@pytest.fixture(scope="session")
def is_vsphere_deployment():
    """Setups cached variable whether it's vsphere deployment or not.

    :returns: Whether is this vsphere deployment (cached).
    :rtype: ``bool``

    """
    try:
        Test.RPM.query('open-vm-tools')
        return True
    except AssertionError:
        pass

    try:
        assert Test.Run.bash("grep -qi vmware /sys/bus/scsi/devices/*/vendor")
        return True
    except AssertionError:
        pass

@pytest.fixture(scope="session")
def ec2_deployment():
    """Setups cached variable whether it's ec2 deployment or not.

    :returns: Whether is this EC2 deployment (cached).
    :rtype: ``bool``

    """
    # The --fail curl argument will cause curl to exit with rc=22 if a server
    # failure occurs (e.g. 403 or 404)
    cmd = 'curl --fail http://169.254.169.254/latest/dynamic/instance-identity/document'
    print "# %s" % cmd
    return subprocess.call(cmd.split()) == 0

@pytest.fixture
def subscription_manager_version():
    """Setups cached variable of version of sub-man

    :returns: SM version from cache
    :rtype: 2-tuple
    """
    sm_rpm_ver = Test.Run.bash("rpm -q --queryformat %{VERSION} subscription-manager")
    assert sm_rpm_ver
    sm_rpm_ver = sm_rpm_ver.stdout
    sm_ver_maj, sm_ver_min, sm_ver_rest = sm_rpm_ver.split(".", 2)
    return int(sm_ver_maj), int(sm_ver_min)

@pytest.fixture
def system_uuid():
    """ Returns system UUID from subscription-manager

    :returns: System UUID
    :rtype: ``str``
    """
    facts = Test.Run.command("subscription-manager facts --list")
    assert facts
    facts = facts.stdout.strip().split("\n")
    for fact in facts:
        name, value = fact.split(":", 1)
        if name == "system.uuid":
            return value.lstrip()

@pytest.fixture
def selinux_enabled():
    """ Detects whether is SElinux enabled or not

    :returns: SElinux status
    :rtype: ``bool``
    """
    return Test.SELinux.enabled

@pytest.fixture
def selinux_getenforce():
    """ Returns current enforcing mode of SELinux

    :returns: SElinux enforcing status
    :rtype: ``str``
    """
    return Test.SELinux.getenforce

@pytest.fixture
def selinux_getenforce_conf():
    """ Returns current enforcing mode of SELinux from config file

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

@pytest.fixture
def selinux_type():
    """ Returns current SELINUX type from config file

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

@pytest.fixture
def rpm_package_list():
    """ Returns list of all installed packages in computer.

    :returns: List of all installed packages in computer.
    :rtype: ``list``
    """
    return Test.RPM.query()

@pytest.fixture
def rpm_package_list_names():
    """ Returns list of all installed packages in computer.

    :returns: List of all installed packages in computer.
    :rtype: ``list``
    """
    return Test.RPM.query(format="%{NAME}")

@pytest.fixture
def rhel_release():
    """Returns RHEL version

    :returns: RHEL version
    :rtype: ``tuple``
    """
    redhat_release_content = Test.Run.command("cat /etc/redhat-release")
    assert redhat_release_content
    redhat_version_field = redhat_release_content.stdout.strip().split(" ")[6]
    class RedhatRelease(object):
        def __init__(self, major, minor, distro="RHEL"):
            self.major = int(major)
            self.minor = int(minor)
            self.distro = distro

        # Compatibility layer
        def __getitem__(self, position):
            if position == 0:
                return str(self.major)
            elif position == 1:
                return str(self.minor)
            else:
                raise KeyError("only 0 and 1 supported")
    #return tuple(redhat_version_field.split(".", 1))
    return RedhatRelease(*redhat_version_field.split(".", 1))

@pytest.fixture
def PATH():
    """ PATH environment variable

    :returns: List of directories in $PATH
    :rtype: ``list``
    """
    return os.environ["PATH"].split(":")

@pytest.fixture
def gpgcheck_enabled():
    """ Whether is GPG check enabled in yum

    :returns: GPG check status
    :rtype: ``bool``
    """
    cfg = ConfigParser()
    cfg.read(["/etc/yum.conf"])
    return int(cfg.get("main", "gpgcheck")) == 1

@pytest.fixture
def chkconfig_list():
    """ Returns list of all services with enablement in each runlevel

    :returns: All services.
    :rtype: ``dict``
    """
    result = {}
    chkconfig = Test.Run.command("chkconfig --list")
    assert chkconfig
    for line in chkconfig.stdout.strip().split("\n"):
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

@pytest.fixture
def service_check():
    """ Produces service-checking fixture """

    class ServiceChecker(object):
        def __init__(self, services):
            self.services = services

        def __call__(self, service, runlevel, active=True):
            return common.services.service_active_in_runlevel(self.services, service, runlevel, active)

    return ServiceChecker(chkconfig_list())

@pytest.fixture
def is_systemd():
    """
        Checks for systemd presence
    """
    try:
        Test.RPM.query("systemd")
        return True
    except AssertionError:
        return False
