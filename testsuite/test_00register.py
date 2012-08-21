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

import common
import pytest
import shutil
import os
from ConfigParser import ConfigParser
import glob
import re
import subprocess

configure_rhsm_tunnel = False
cwd = os.getcwd()

def test_audreyvars(audreyvars):
    """
        This test checks for presence of audrey environment variables.

        Args:
            audreyvars: Dict of audrey environment variables

        Raises:
            AssertionError
    """
    assert len(audreyvars) > 0

def test_gpg_key_import_release():
    """
        This test imports redhat-release GPG certificate

        Raises:
            AssertionError
    """
    common.run("rpm --import /etc/pki/rpm-gpg/RPM-GPG-KEY-redhat-release")

def test_gpg_key_import_beta(audreyvars):
    """
        This test imports redhat-beta GPG certificate if it's wanted (audreyvars[IMPORT_GPG_BETA_KEY]).
        Otherwise, it's skipped.

        Args:
            audreyvars: Dict of audrey environment variables

        Raises:
            AssertionError
    """
    betakey = audreyvars.get("IMPORT_GPG_BETA_KEY", "false").lower()
    if betakey == "true":
        common.run("rpm --import /etc/pki/rpm-gpg/RPM-GPG-KEY-redhat-beta")
    else:
        pytest.skip(msg='Not importing beta key')

def test_import_rhel_product_cert(audreyvars, ec2_deployment):
    """
        This test imports RHEL product certificates if it's desired.

        Args:
            audreyvars: Dict of audrey environment variables
            ec2_deployment (bool): Whether is this machine in EC2 or not

        Raises:
            AssertionError, Failed
    """
    if ec2_deployment and not os.path.isfile('/etc/pki/product/69.pem'):
        os.chdir('/var/audrey/tooling/user/%s' % audreyvars.get("RHEL_PRODUCT_CERT_TASK", "RHEL_PRODUCT_CERT"))
        output = common.run('rpm -qf /etc/redhat-release --qf "%{release}"')
        (major, minor, garbage) = output.split('.', 2)
        pem_file = '%s.%s-%s.pem' % (major, minor, os.uname()[-1])
        if os.path.isfile(pem_file):
            if not os.path.isdir('/etc/pki/product'):
                os.mkdir('/etc/pki/product')
            shutil.copy(pem_file, '/etc/pki/product/69.pem')
        else:
            pytest.fail(msg="Unable to find PEM file for %s.%s-%s" % (major, minor, garbage))
    else:
        pytest.skip(msg='Not importing RHEL Product key')

def test_return_to_default_directory():
    """
        This test just assures that we are in right directory
    """
    os.chdir(cwd)

def test_setup_tunnel(audreyvars, katello_discoverable, tunnel_requested):
    """
        This test configures SSH tunnel if it's desired.

        Args:
            audreyvars: Dict of audrey environment variables
            katello_discoverable (bool): Whether is katello service discoverable or not
            tunnel_requested (bool): Whether was tunnel requested or not

        Raises:
            AssertionError
    """
    if not katello_discoverable and tunnel_requested:
        print "Configuring tunnel"
        # Backup the /etc/hosts file
        shutil.copy("/etc/hosts", "/etc/hosts.orig")
        # Modify /etc/hosts to support tunneling
        fp = open("/etc/hosts", "r+")
        buf = fp.read()
        fp.seek(0)
        fp.write(buf)
        fp.write("%s %s\n" % (audreyvars["SSH_TUNNEL_IP"], audreyvars["KATELLO_HOST"]))
        fp.close()

        # Replace the katello port with the provided tunneled katello port
        # In case variable names changed, make noise if we don't find the expected
        # variable
        assert audreyvars.has_key("KATELLO_PORT")
        os.environ["AUDREY_VAR_KATELLO_REGISTER_KATELLO_PORT"] = os.environ.get("AUDREY_VAR_KATELLO_REGISTER_SSH_TUNNEL_KATELLO_PORT", "8080")
        configure_rhsm_tunnel = True
    else:
        pytest.skip(msg='Not configuring tunnel')

def test_setup_releasever(audreyvars):
    """
        This test sets up yum releasever if it's desired

        Args:
            audreyvars: Dict of audrey environment variables

        Raises:
            KeyError, IOError
    """
    if not audreyvars.get("RELEASEVER", "Auto").lower() in ["", "auto"]:
        if not os.path.isdir('/etc/yum/vars'):
            os.mkdir('/etc/yum/vars')
        fp = open("/etc/yum/vars/releasever", "w+")
        fp.write(audreyvars["RELEASEVER"])
        fp.close()
    else:
        pytest.skip(msg='Not customizing yum releasever')

def test_import_certificate(audreyvars):
    """
        This test imports Candlepin consumer certificate.

        Args:
            audreyvars: Dict of audrey environment variables

        Raises:
            AssertionError
    """
    cert_rpm = common.s_format("http://{KATELLO_HOST}:{KATELLO_PORT}/pub/candlepin-cert-consumer-{KATELLO_HOST}-1.0-1.noarch.rpm", audreyvars)
    cmd = "rpm -ivh %s" % cert_rpm
    common.run(cmd)

def test_tunnel_rhsm(audreyvars, subscription_manager_version):
    """
        This test sets up a RHSM tunnel, if it's desired.

        Args:
            audreyvars: Dict of audrey environment variables
            subscription_manager_version: 2-tuple of major and minor version

        Raises:
            AssertionError, IOError
    """
    if not configure_rhsm_tunnel:
        pytest.skip(msg='Not setting up a tunnel')
    sm_ver_maj, sm_ver_min = subscription_manager_version
    rhsm_baseurl = "https://%s:%s/pulp/repos" % (audreyvars["KATELLO_HOST"], audreyvars["SSH_TUNNEL_PULP_PORT"])
    server_port = audreyvars["SSH_TUNNEL_PULP_PORT"]
    if sm_ver_maj <= 0:
        if sm_ver_min < 96:
            rhsm_conf = '/etc/rhsm/rhsm.conf'
            cfg = ConfigParser()
            cfg.read([rhsm_conf])
            cfg.set('rhsm', 'baseurl', rhsm_baseurl)
            cfg.set('server', 'port', server_port)
            # Save config
            fd = open(rhsm_conf, 'wa+')
            cfg.write(fd)
            fd.close()
        else:
            common.run('subscription-manager config --rhsm.baseurl=%s' % rhsm_baseurl)
            common.run('subscription-manager config --server.port=%s' % server_port)

def test_disable_rhui(audreyvars, ec2_deployment):
    """
        This test disables RHUI, if it's desired.

        Args:
            audreyvars: Dict of audrey environment variables
            ec2_deployment (bool): Whether is this machine in EC2 or not.

        Raises:
            AssertionError
    """
    if ec2_deployment and audreyvars.get("DISABLE_RHUI", "True").lower() == "true":
        try:
            # Disable any yum repoid's matchin 'rhui-*'
            common.run(common.s_format('yum-config-manager --disable "rhui-*"', os.environ))
        except OSError, e:
            # Disable all repositories defined in files matching 'redhat-*.repo'
            for repo_file in glob.glob("/etc/yum.repos.d/redhat-*.repo"):
                common.update_yum_repo(repo_file, enabled=False)

        # Disable the rhui-lb plugin
        common.update_yum_plugin('rhui-lb.conf', enabled=False)
    else:
        pytest.skip(msg='Not disabling RHUI')

def test_katello_register(audreyvars, subscription_manager_version):
    """
        This test registers system into Katello server.

        Args:
            audreyvars: Dict of audrey environment variables
            subscription_manager_version: 2-tuple of major and minor version

        Raises:
            AssertionError
    """
    org = audreyvars["KATELLO_ORG"]
    activation_key = audreyvars.get("ACTIVATION_KEY", "").strip()
    auto_subscribe = audreyvars.get("AUTO_SUBSCRIBE", "false").lower() == "true"
    username = audreyvars["KATELLO_USER"]
    password = audreyvars["KATELLO_PASS"]
    kat_env = audreyvars["KATELLO_ENV"]
    sm_ver_maj, sm_ver_min = subscription_manager_version

    cmd = "subscription-manager register"

    if sm_ver_maj <= 0:
        if sm_ver_min < 96:
            if auto_subscribe:
                cmd += " --username=%s --password=%s" % (username, password)
                cmd += " --autosubscribe"
            elif activation_key != "" and sm_ver_min >= 95:
                cmd += " --activationkey=%s" % activation_key
            else:
                pass # determine and print error condition to stdout
        else:
            cmd += " --org=%s" % org
            if auto_subscribe:
                cmd += " --username=%s --password=%s" % (username, password)
                cmd += " --env=%s" % kat_env
                cmd += " --autosubscribe"
            elif activation_key != "":
                cmd += " --activationkey=%s" % activation_key
            else:
                pass # determine and print error condition to stdout
    common.run(cmd)

    # VERIFICATION
    # Test whether registration succeeded
    common.run('subscription-manager refresh')
