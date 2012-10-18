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
import net

import pytest

from urllib2 import urlopen, HTTPError, URLError
try:
    import json
except ImportError:
    import simplejson as json

def poll_task_state(server, task_uuid, login, password):
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
    request = net.make_auth_request("https://%s/katello/api/systems/tasks/%s" % (server, task_uuid), login, password)
    response = urlopen(request)
    data = json.loads("\n".join(response.readlines()))
    return str(data["state"])

def query_remote_install(server, uuid, login, password, package):
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
    request = net.make_auth_request("https://%s/katello/api/systems/%s/packages" % (server, uuid), login, password)
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
            pytest.fail(msg="Error when querying installation of package %s with HTTP code %d: %s" % (package, int(e.code), e))
    # get the task uuid
    task_uuid = json.loads("\n".join(response.readlines()))["uuid"]
    # poll it
    state = ""
    # List of allowed states
    ok_states = ["waiting", "running", "finished"]
    while state != "finished":
        state = poll_task_state(server, task_uuid, login, password)
        if state not in ok_states:
            pytest.fail(msg="Installation of package %s failed when task went to state '%s'" % (str(package), state))
    # Package is installed, let's verify it
    shell.run("rpm -q %s" % package)
