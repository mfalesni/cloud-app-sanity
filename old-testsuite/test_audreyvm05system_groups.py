#!/usr/bin/env python2
#   Author(s): James Laska <jlaska@redhat.com>
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

""" This module contains tests which are supposed to test remote control
    Katello -> guest computer
"""

import re
import pytest
import common.yum
import common.katello

@pytest.mark.skipif("True")
def test_system_group_query(audreyvars, tunnel_requested):
    """ Tests whether katello is capable of exporting available system groups
        via the API.

    :param audreyvars: Audrey environemnt variables
    :type audreyvars: ``dict``
    :param tunnel_requested: Whether was tunnel requested or not
    :type tunnel_requested: bool

    :raises: pytest.Skipped, pytest.Failed
    """
    server = audreyvars["KATELLO_HOST"]
    login = audreyvars.get("KATELLO_USER", "admin")
    org = audreyvars.get("KATELLO_ORG", "redhat")
    password = audreyvars.get("KATELLO_PASS", "admin")

    # If using a tunnel to access ec2, an alternative port is needed
    if tunnel_requested:
        port = audreyvars.get("SSH_TUNNEL_KATELLO_PORT", 1443)
    else:
        port = audreyvars.get("KATELLO_PORT", 443)

    common.katello.system_group_query(server, port, org, login, password)

@pytest.mark.skipif("True")
def test_system_group_create(audreyvars, tunnel_requested, system_groups):
    """ Installs packages specified in YUM_REMOTE_INSTALL into this system via
        remote request through Katello server to check whether there aren't any issues.

    :param audreyvars: Audrey environemnt variables
    :type audreyvars: ``dict``
    :param tunnel_requested: Whether was tunnel requested or not
    :type tunnel_requested: bool
    :param system_groups: A list of system_groups that apply to the current instance
    :type system_groups: list

    :raises: pytest.Skipped, pytest.Failed
    """
    server = audreyvars["KATELLO_HOST"]
    login = audreyvars.get("KATELLO_USER", "admin")
    org = audreyvars.get("KATELLO_ORG", "redhat")
    password = audreyvars.get("KATELLO_PASS", "admin")

    # If using a tunnel to access ec2, an alternative port is needed
    if tunnel_requested:
        port = audreyvars.get("SSH_TUNNEL_KATELLO_PORT", 1443)
    else:
        port = audreyvars.get("KATELLO_PORT", 443)

    # Query existing system groups
    current_group_names = [g.get('name') for g in common.katello.system_group_query(server, port, org, login, password)]

    # Determine whether groups were created
    new_group_ids = []
    for group_name in system_groups:
        if group_name not in current_group_names:
            result_dict = common.katello.system_group_create(server, port, org, login, password, group_name)
            new_group_ids.append(result_dict.get('id'))

    if len(new_group_ids) == 0:
        pytest.skip(msg="System groups already exist, no groups created")

@pytest.mark.skipif("True")
def test_system_group_add_system(audreyvars, system_uuid, tunnel_requested, system_groups):
    """ Installs packages specified in YUM_REMOTE_INSTALL into this system via
        remote request through Katello server to check whether there aren't any issues.

    :param audreyvars: Audrey environemnt variables
    :type audreyvars: ``dict``
    :param system_uuid: This system's unique ID for Katello
    :type system_uuid: ``str``
    :param tunnel_requested: Whether was tunnel requested or not
    :type tunnel_requested: bool
    :param system_groups: A list of system_groups that apply to the current instance
    :type system_groups: list

    :raises: pytest.Skipped, pytest.Failed
    """
    server = audreyvars["KATELLO_HOST"]
    login = audreyvars.get("KATELLO_USER", "admin")
    org = audreyvars.get("KATELLO_ORG", "redhat")
    password = audreyvars.get("KATELLO_PASS", "admin")

    # If using a tunnel to access ec2, an alternative port is needed
    if tunnel_requested:
        port = audreyvars.get("SSH_TUNNEL_KATELLO_PORT", 1443)
    else:
        port = audreyvars.get("KATELLO_PORT", 443)

    # Locate existing system groups, and add system
    for group_name in system_groups:
        result = common.katello.system_group_query(server, port, org, login, password, group_name)
        assert len(result) > 0, "System group '%s' not found" % group_name
        group_id = result[0].get('id')
        common.katello.system_group_add_system(server, port, org,
                system_uuid, login, password,
                group_id)
