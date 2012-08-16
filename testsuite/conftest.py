#!/usr/bin/env python2
#   Author(s):	Milan Falesnik <mfalesni@redhat.com>
#				James Laska <jlaska@redhat.com>
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
import subprocess
import common

def pytest_funcarg__audreyvars(request):
	'''
	Setups variables for testing
	'''
	result = {}
	for key in os.environ:
		if key.startswith("AUDREY_VAR_KATELLO_REGISTER_"):
			result[re.sub("^AUDREY_VAR_KATELLO_REGISTER_", "", key)] = os.environ[key]

	return result


def pytest_funcarg__katello_discoverable(request):
	'''Returns boolean (True of False) to indicate whether the provided katello
	server is accessible'''
	cmd = "ping -q -c5 %s" % request.getfuncargvalue("audreyvars")["KATELLO_HOST"]
	print "# %s" % cmd
	return subprocess.call(cmd.split()) == 0

def pytest_funcarg__tunnel_requested(request):
	''' Determines whether setting up SSH tunnel is requested '''
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
	'''
	Setups cached variable whether it's ec2 deployment or not.
	'''
	return request.cached_setup(setup=setup_ec2_deployment, scope="module")

def setup_ec2_deployment():
	'''Returns boolean True of False to indicate whether the current system is
	   an ec2 image'''
	cmd = 'curl --silent http://169.254.169.254/latest/dynamic/instance-identity/document'
	print "# %s" % cmd
	return subprocess.call(cmd.split()) == 0

def pytest_funcarg__subscription_manager_version(request):
    '''
    Setups cached variable of version of sub-man
    '''
    return request.cached_setup(setup=setup_subscription_manager_version, scope="module")

def setup_subscription_manager_version():
    sm_rpm_ver = common.run("rpm -q --queryformat %{VERSION} subscription-manager")
    sm_ver_maj, sm_ver_min, sm_ver_rest = sm_rpm_ver.split(".", 2)
    return int(sm_ver_maj), int(sm_ver_min)