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

"""
    This file contains tests around SSL
"""

import pytest
import common.ssl

class TestSSL(object):
    REQUIRED_BITS = 2048
    FORBIDDEN_HASHES = ["md5"]

    @pytest.fixture
    def key_strength(self):
        """
            Fixture, providing SSL key strength.
        """
        config = common.ssl.openssl_config_get_section("req")
        return int(config["default_bits"])

    @pytest.fixture
    def default_hash(self):
        """
            Fixture, providing default hash function.
        """
        config = common.ssl.openssl_config_get_section("req")
        return config["default_md"]

    def test_default_key_strength(self, key_strength):
        """
        Confirm that the default SSL certificate generation strength is at least
        2048 bits.

        :raises: pytest.Failed
        """
        assert key_strength >= TestSSL.REQUIRED_BITS, "Default bit length of certificate is insufficient (%d < %d)" % (key_strength, TestSSL.REQUIRED_BITS)

    def test_default_hash_function(self, default_hash):
        """
        Confirm default hashing method is not md5

        :raises: pytest.Failed
        """
        assert default_hash.lower() not in TestSSL.FORBIDDEN_HASHES, "Bad message digest function (%s)!" % default_hash
