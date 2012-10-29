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
import common.ssl

def test_default_key_strength():
    """ Checks for SSL certificate generation strength

    :raises: pytest.Failed
    """
    config = common.ssl.openssl_config_get_section("req")
    bits = int(config["default_bits"])
    try:
        assert bits >= 2048
    except AssertionError:
        pytest.fail(msg="Default bit length of certificate is insufficient")

def test_default_hash_function():
    """ tests for insufficient hashing functions in config

    :raises: pytest.Failed
    """
    config = common.ssl.openssl_config_get_section("req")
    hashf = config["default_md"]
    try:
        assert hashf.lower() not in ["md5"]
    except AssertionError:
        pytest.fail(msg="Bad message digest function!")
