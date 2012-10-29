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

""" This module contains tests which are supposed to test remote control
    Katello -> guest computer
"""

import pytest
import common.katello

def test_install_packages_remote(audreyvars, system_uuid, tunnel_requested):
    """ Installs packages specified in YUM_REMOTE_INSTALL into this system via
        remote request through Katello server to check whether there aren't any issues.

    :param audreyvars: Audrey environemnt variables
    :type audreyvars: ``dict``
    :param system_uuid: This system's unique ID for Katello
    :type system_uuid: ``str``
    :param tunnel_requested: Whether was tunnel requested or not
    :type tunnel_requested: bool

    :raises: pytest.Skipped, pytest.Failed
    """
    packages = audreyvars.get("YUM_REMOTE_INSTALL", "").strip()
    server = audreyvars["KATELLO_HOST"]
    login = audreyvars.get("KATELLO_USER", "admin")
    password = audreyvars.get("KATELLO_PASS", "admin")

    # If using a tunnel to access ec2, an alternative port is needed
    if tunnel_requested:
        port = audreyvars.get("SSH_TUNNEL_KATELLO_PORT", 1443)
    else:
        port = audreyvars.get("KATELLO_PORT", 443)

    # Were packages requested for install?
    if packages != "":
        packages = packages.split(" ")
    else:
        pytest.skip(msg="No packages marked for remote install")

    # Initiate remote install for requested packages
    for package in packages:
        common.katello.query_remote_install(server, port, system_uuid, login, password, package)
