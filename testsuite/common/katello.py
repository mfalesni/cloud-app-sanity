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

import pytest
import common.shell
import common.net
from urllib2 import urlopen, quote, HTTPError, URLError

try:
    import json
except ImportError:
    import simplejson as json

def poll_task_state(server, port, task_uuid, login, password):
    """ This function returns state of task with given UUID.
        Useful when polling certain task if finished or not.

    :param server: Katello server to poll on.
    :type server: ``str``
    :param port: Katello port to poll on.
    :type port: ``str``
    :param task_uuid: Checked task's unique ID
    :type task_uuid: ``str``
    :param password: Login password into Katello server
    :type password: ``str``
    :param package: Package to install into system
    :type package: ``str``

    :returns: Reported task state
    :rtype: ``str``
    """
    request = common.net.make_auth_request("https://%s:%s/katello/api/systems/tasks/%s" % (server, port, task_uuid), login, password)
    response = urlopen(request)
    data = json.loads("\n".join(response.readlines()))
    return str(data["state"])

def system_group_create(server, port, org, login, password, group_name):
    """ This function creates a system group via a katello API request.

    :param server: Remote Katello server
    :type server: ``str``
    :param port: Remote Katello port
    :type port: ``str``
    :param org: Katello organization
    :type org: ``str``
    :param login: Login name into Katello server
    :type login: ``str``
    :param password: Login password into Katello server
    :type password: ``str``
    :param group_name: Name of the system group to create
    :type group_name: ``str``

    :raises: pytest.Failed
    """
    # Prepare the request
    # POST /api/organizations/:organization_id/system_group
    request = common.net.make_auth_request("https://%s:%s/katello/api/organizations/%s/system_groups" % (server, port, org), login, password)
    request.add_header("content-type", "application/json")
    body = json.dumps({'system_group': {'name':group_name, 'max_systems':'-1'}})
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
            pytest.fail(msg="Error when creating system_group %s with HTTP code %d: %s" % (group_name, int(e.code), e))

    return json.loads(response.read())

def system_group_add_system(server, port, org, uuid, login, password, group_id):
    """ This function adds a system to a specified system group

    :param server: Remote Katello server
    :type server: ``str``
    :param port: Remote Katello port
    :type port: ``str``
    :param org: Katello organization
    :type org: ``str``
    :param uuid: Target machine UUID
    :type uuid: ``str``
    :param login: Login name into Katello server
    :type login: ``str``
    :param password: Login password into Katello server
    :type password: ``str``
    :param group_id: Id of the system group to create
    :type group_id: ``str``

    :raises: pytest.Failed
    """
    # Prepare the request
    # POST /api/organizations/:organization_id/system_group
    request = common.net.make_auth_request("https://%s:%s/katello/api/organizations/%s/system_groups/%s/add_systems" \
            % (server, port, org, group_id), login, password)
    request.add_header("content-type", "application/json")
    body = json.dumps({'system_group': {'system_ids':[uuid]}})
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
            pytest.fail(msg="Error when adding system '%s' to group id '%s' with HTTP code %d: %s" % (uuid, group_id, int(e.code), e))

    return json.loads(response.read())

def system_group_query(server, port, org, login, password, query_name=None):
    # Prepare the request
    query_url = "https://%s:%s/katello/api/organizations/%s/system_groups/" % (server, port, org)
    if query_name is not None:
        query_url = "%s?name=%s" % (query_url, quote(query_name))

    request = common.net.make_auth_request(query_url, login, password)

    try:
        # send the request
        response = urlopen(request)
    except HTTPError, e:
        if int(e.code) in [202]:
            response = e # To work in RHEL5
        else:
            pytest.fail(msg="Error when querying system groups with HTTP code %d: %s" % (int(e.code), e))
    return json.loads("\n".join(response.readlines()))

def query_remote_install(server, port, uuid, login, password, package):
    """ This function installs package into guest system via Katello request.
        Basically, it tells Katello "Hey, Katello, install these packages into machine with that UUID"

    :param server: Remote Katello server
    :type server: ``str``
    :param port: Remote Katello port
    :type port: ``str``
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
    request = common.net.make_auth_request("https://%s:%s/katello/api/systems/%s/packages" % (server, port, uuid), login, password)
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
        state = poll_task_state(server, port, task_uuid, login, password)
        if state not in ok_states:
            pytest.fail(msg="Installation of package %s failed when task went to state '%s'" % (str(package), state))
    # Package is installed, let's verify it
    common.shell.run("rpm -q %s" % package)
