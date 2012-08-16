from string import Template
import subprocess
import shlex
import re
from ConfigParser import ConfigParser
import os

def run(cmd):
	print "# %s" % cmd
	if isinstance(cmd, str):
		cmd = shlex.split(cmd)
	p_open = subprocess.Popen(cmd,
					stdout=subprocess.PIPE,
					stderr=subprocess.STDOUT)
	(stdout, stderr) = p_open.communicate()
	assert p_open.returncode == 0
	return stdout

def s_format(s, dct):
	if hasattr(s, 'format'):
		return s.format(**dct)
	else:
		# convert python-2.6 format to something 2.4 can handle
		return Template(re.sub(r'{([^}]+)}', '$\\1', s)).substitute(dct)

def update_yum_config(repo_file, enabled=True):
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

def update_yum_repo(repo_file, enabled=True):
	if not repo_file.startswith('/'):
		repo_file = '/etc/yum.repos.d/%s' % repo_file
	if not repo_file.endswith('.repo'):
		repo_file = '%s.repo' % repo_file
	update_yum_config(repo_file, enabled)

def update_yum_plugin(plugin_conf, enabled=True):
	if not plugin_conf.startswith('/'):
		plugin_conf = '/etc/yum/pluginconf.d/%s' % plugin_conf
	if not plugin_conf.endswith('.conf'):
		plugin_conf = '%s.conf' % plugin_conf
	update_yum_config(plugin_conf, enabled)