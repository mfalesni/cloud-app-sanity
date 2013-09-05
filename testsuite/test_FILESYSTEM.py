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

import os
import stat
import sys
import fnmatch

""" Filesystem checking tests """
class TestFileSystem(object):
    @Test.Fixture
    def world_writable_whitelist(self):
        """
            Reads a whitelist of files that can be world_writable.

        :returns: Whitelist of world-writable files
        """
        try:
            f = open("parametrized/world_writable_whitelist", "r")
        except IOError:
            f = open("../parametrized/world_writable_whitelist", "r") # For testing purposes

        data = [line.strip() for line in f.readlines()]
        f.close()
        return data

    @Test.Fixture
    def ignore_patterns(self):
        """
            Reads a list of ignore patterns which won't be tested.

        :returns: List of ignore patterns
        """
        try:
            f = open("parametrized/fs_ignore_patterns", "r")
        except IOError:
            f = open("../parametrized/fs_ignore_patterns", "r") # For testing purposes

        data = [line.strip() for line in f.readlines()]
        f.close()
        return data


    def fmt_mode_str(self, st_mode):
        """ ???
            Does the formatting of props.
        """
        # Type
        ftype_alias = dict(REG='-', FIFO='p', UID='s', GID='s', VTX='t')
        mode_str = '-'
        for ftype in ['DIR', 'CHR', 'BLK', 'FIFO', 'LNK', 'SOCK',]:
            func = getattr(stat, 'S_IS%s' % ftype)
            if func(st_mode):
                mode_str = ftype_alias.get(ftype, ftype[:1].lower())
                break

        for level in "USR", "GRP", "OTH":
            for perm in "R", "W", "X":
                if st_mode & getattr(stat,"S_I"+perm+level):
                    mode_str += perm.lower()
                else:
                    mode_str += '-'

        # sticky bit
        for (count, fsticky) in enumerate(['UID', 'GID', 'VTX'], 1):
            if st_mode & getattr(stat,"S_IS"+fsticky):
                pos = count * 3
                fchar = ftype_alias.get(fsticky, fsticky[:1].lower())
                mode_str = mode_str[:pos] + fchar + mode_str[pos+1:]

        return mode_str + '.'

    def test_check_permissions_and_broken_symlinks(self, world_writable_whitelist, ignore_patterns):
        """ This test checks whether there are some files with unwanted props in FS.
            Looks for broken symlinks and world-writable files.

        :raises: ``pytest.Failed``
        """
        stack = []  # Used for storing directories to parse
        starting_dir = "/"
        failed = False

        # Helper functions
        is_dir = lambda x: stat.S_ISDIR( x.st_mode)
        is_lnk = lambda x: stat.S_ISLNK(x.st_mode)
        is_sock = lambda x: stat.S_ISSOCK(x.st_mode)
        is_chr = lambda x: stat.S_ISCHR(x.st_mode)
        is_blk = lambda x: stat.S_ISBLK(x.st_mode)
        is_reg = lambda x: stat.S_ISREG(x.st_mode)
        is_world_writable = lambda x: stat.S_IWOTH & x.st_mode

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

                # Skip this file/dir, has the wrong pattern
                if any([fnmatch.fnmatch(path, p) for p in ignore_patterns]):
                    sys.stdout.write("[ignoring] %s\n" % (path,))
                    continue

                info = os.lstat(path)
                if is_lnk(info):
                    # Check if it's broken or not
                    if not Test.Shell.exists_in_path(os.readlink(path), os.path.abspath(directory)):
                        sys.stderr.write("[broken-symlink] %s -> %s\n" % (path, os.readlink(path)))
                        failed = True
                else:
                    if is_dir(info):
                        stack.append(path)

                    # FIXME - determine whether file is truly writable (parent dir
                    # may not be readable)
                    # Check its permissions, if wrong, append it
                    if is_world_writable(info):
                        # If the path isn't on the whitelist ... we found a failure
                        if not any([fnmatch.fnmatch(path, p) for p in world_writable_whitelist]):
                            sys.stderr.write("[world-writable] %s %s\n" % (self.fmt_mode_str(info.st_mode), path))
                            failed = True
        if failed:
            Test.Fail(msg="Test failed")

