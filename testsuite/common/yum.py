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

import pytest

from ConfigParser import ConfigParser

def install(package_name):
    """ Does the 'yum install <package>' command.

    :param package_name: Name of the package to install (eg. katello-all)
    :type package_name: str

    :raises: AssertionError
    """
    # Install it
    shell.run("yum -y install %s" % (package_name))
    # Verify it
    shell.run("rpm -q %s" % (package_name))

def remove(package_name):
    """ Does the 'yum remove <package>' command.

    :param package_name: Name of the package to be removed (eg. katello-all)
    :type package_name: str

    :raises: AssertionError
    """
    # Remove it
    shell.run("yum -y remove %s" % (package_name))
    # Verify it
    shell.run("rpm -q %s" % (package_name), errorcode=1)

def update_config(repo_file, enabled=True):
    """Enables or disables all sections in Yum config files

    :param repo_file: Config file, which should be processed
    :type repo_file: str
    :param enabled: Whether to enable or disable
    :type enabled: bool

    """
    if os.path.isfile(repo_file):
        cfg = ConfigParser()
        cfg.read([repo_file])
        save_changes = False
        for section in cfg.sections():
            if cfg.has_option(section, 'enabled'):
                save_changes = True
                if enabled:
                    cfg.set(section, 'enabled', 1)
                else:
                    cfg.set(section, 'enabled', 0)
        if save_changes:
            fd = open(repo_file, 'rwa+')
            cfg.write(fd)
            fd.close()
    else:
        pytest.fail(msg="%s was not found!" % repo_file)

def update_repo(repo_file, enabled=True):
    """Enables or disables all sections in Yum repository files

    :param repo_file: Repo file, which should be processed
    :type repo_file: str
    :param enabled: Whether to enable or disable
    :type enabled: bool
    """
    if not repo_file.startswith('/'):
        repo_file = '/etc/yum.repos.d/%s' % repo_file
    if not repo_file.endswith('.repo'):
        repo_file = '%s.repo' % repo_file
    update_yum_config(repo_file, enabled)

def update_plugin(plugin_conf, enabled=True):
    """Enables or disables all sections in Yum plugin config files

    :param repo_file: Config file, which should be processed
    :type repo_file: str
    :param enabled: Whether to enable or disable
    :type enabled: bool
    """
    if not plugin_conf.startswith('/'):
        plugin_conf = '/etc/yum/pluginconf.d/%s' % plugin_conf
    if not plugin_conf.endswith('.conf'):
        plugin_conf = '%s.conf' % plugin_conf
    update_yum_config(plugin_conf, enabled)
