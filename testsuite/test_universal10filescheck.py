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
import stat
import sys
from re import compile as _

""" Filesystem checking tests """

def test_check_permissions_and_broken_symlinks():
    """ This test checks whether there are some files with unwanted props in FS.
        Looks for broken symlinks and world-writable files.

    :raises: pytest.Failed
    """
    stack = []  # Used for storing directories to parse
    starting_dir = "/"
    ignored_patterns = [_("^/proc")]    # List of all ignored patterns ... use _ as re.compile
    failed = False
    # Helper functions
    isdir = lambda x: stat.S_ISDIR( x.st_mode)
    islnk = lambda x: stat.S_ISLNK(x.st_mode)
    world_writable = lambda x: stat.S_IWOTH & x.st_mode
    # Start it up
    stack.append(starting_dir)
    while len(stack) > 0:
        # Get actual directory
        directory = stack.pop()
        # Parse through it
        for entry in os.listdir(directory):
            # Stat it
            path = "%s/%s" % (directory, entry)
            if path.startswith("//"):   # Strip beginning // because of root dir
                path = path[1:]
            for pattern in ignored_patterns:
                if pattern.search(path):
                    continue    # Skip this file/dir, has the wrong pattern
            info = os.lstat(path)
            if world_writable(info):
                # Check its permissions, if wrong, append it
                sys.stderr.write("WW %s\n" % path)
                failed = True
            if islnk(info):
                # Check if it's broken or not
                if not common.exists_in_path(os.readlink(path), os.path.abspath(directory)):
                    sys.stderr.write("BS %s\n" % path)
                    failed = True
            elif isdir(info):
                stack.append(path)
    if failed:
        pytest.fail(msg="Test failed")
        