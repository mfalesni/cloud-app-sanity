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
import common.yum

def test_install_package_locally_from_yum(audreyvars):
    """ This test does local install of package (by yum command).
        It takes a list of packages (separated by spaces) and installs them one by one.

    :param audreyvars: Dict of Audrey environment variables
    :type audreyvars: dict
    """
    packages = audreyvars.get("YUM_LOCAL_INSTALL", "").strip()
    if packages != "":
        packages = packages.split(" ")
    else:
        pytest.skip(msg="No packages marked for local install")
    for package in packages:
        print "Installing package %s" % package
        common.yum.install(package)

