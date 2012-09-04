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

import common
import pytest
import os



def test_import_ssh_certificate(audreyvars):
    """ Imports SSH certificate from the files, urls, everything.
        Files are specified in JENKINS_SSH_KEY_LOCATION.
        If it is None, nothing happens

    :param audreyvars: Audrey environment variables
    :type audreyvars: dict
    """
    JENKINS_SSH_KEY_LOCATION = audreyvars.get("JENKINS_SSH_KEY_LOCATION", "None")
    JENKINS_SSH_DIR = audreyvars.get("JENKINS_SSH_DIR", "/root/.ssh")
    if JENKINS_SSH_KEY_LOCATION.lower() == "none":
        # Key is not present, skipping
        pytest.skip(msg="SSH key is not present, skipping")
    # Create JENKINS_SSH_DIR
    if not os.path.isdir(JENKINS_SSH_DIR):
        common.mkdir(JENKINS_SSH_DIR)
    # Split them into array
    locations = JENKINS_SSH_KEY_LOCATION.split("]]]")
    for location in locations:
        # break it into source and filename
        location = location.split("[[[")
        # Prepare variable to store file name
        target = None
        if len(location) == 2:
            target = target = "%s/%s" % (JENKINS_SSH_DIR, location[1]) # Use provided file name
        location = location[0]
        if not location.startswith("/"):
            # Key is file or URL
            if location.startswith("http"):
                # It's an URL
                if target == None:
                    target = "%s/%s" % (JENKINS_SSH_DIR, common.filename_from_url(location))
                common.download_file(location, target, True)
            else:
                # Key is file in local directory
                filename = "%s/KATELLO_REGISTER/%s" % (common.audrey_service_path, location)
                if target == None:
                    target = "%s/%s" % (JENKINS_SSH_DIR, location)
                if not os.path.isfile(filename):
                    pytest.fail(msg="Unable to find file '%s'" % filename)
                common.copy(filename, target)
        else:
            # It's a file somewhere in filesystem
            if not os.path.isfile(filename):
                pytest.fail(msg="Unable to find file '%s'" % filename)
            if target == None:
                target = "%s/%s" % (JENKINS_SSH_DIR, os.path.basename(location))
            common.copy(location, target)           
        # Verify that key is in place
        if not os.path.isfile(target):
            pytest.fail(msg="Importing the key was unsuccessful, key is not present in '%s'" % target)
        # Add the key into authorized keys
        authkeys = "%s/authorized_keys" % JENKINS_SSH_DIR
        common.append_file(authkeys, target, True)
        # Verify again that the file exists
        # Verify that key is in place
        if not os.path.isfile(authkeys):
            pytest.fail(msg="Importing the key was unsuccessful, file '%s' does not exist" % authkeys)
        # And now for SELinux to work (RHEL5 doesn't matter, but RHEL6 needs this very much)
        common.run("restorecon -R -v %s" % JENKINS_SSH_DIR)