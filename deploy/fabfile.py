import os
import sys

from fabric.api import env, settings
from fabric.api import sudo, run, local, put

import ec2

TMP_PATH = '/tmp/'
HOME_DIR = '/home/jhull/workspace/kickbacker/kb'
HOSTS = {	
			'jeffdev' : {   'user': 'jhull',
							'host': 'office.buzzient.com:34343'
						  }	,

			'web1' : { 'user':'ec2-user',
						'host':'23.23.78.193', 
						'key': '/home/jhull/.ssh/jeffec2.pem'
			},
		}

env.key_filename = '/home/jhull/.ssh/jeffec2.pem'

def host(hostname):
	env.hosts.append("%s@%s" % ( HOSTS[hostname]['user'], \
							HOSTS[hostname]['host']))

def ssh(host):
	local('ssh -i %s %s@%s' % ( HOSTS[host]['key'],
								HOSTS[host]['user'],
								HOSTS[host]['host'],
								) )

def deploy_web():

	# Create New Instance
	instance = ec2.create_new_instance()

	# Scrub past IP record from known_hosts
	local("ssh-keygen -R %s" % (instance.ip_address) )

	# Set Env Host String
	env.host_string = "ec2-user@%s" % (instance.ip_address) 

	# Install Web
	install_web()

	return True


def install_web():

	# Create User
	user = 'kickbacker'
	remote_home_dir = '/home/' + user 
	
	with settings(warn_only=True):
		sudo('useradd -U -m %s' % user)

	# Install packages with yum
	sudo('yum install -y python-devel gcc')

	# Install pip
	sudo('curl -O http://pypi.python.org/packages/source/p/pip/pip-1.0.tar.gz')
	run('tar xvfz pip-1.0.tar.gz')
	sudo('cd pip-1.0 && python setup.py install')

	run('echo $PYTHONPATH')

	# Install virtualenv 
	sudo('pip install virtualenv')
	venv_name = '%s-env' % user
	venv = os.path.join(remote_home_dir, venv_name)
	sudo('virtualenv --no-site-packages %s' % venv)

	run('echo $PYTHONPATH')

	# Activate Virtual Env
	#sudo('source %s/bin/activate' % venv)

	
	# Install python requirements
	put('requirements.txt', remote_home_dir, use_sudo=True)
	sudo('%s/bin/pip install -r %s/requirements.txt' % (venv, remote_home_dir))
	
	# Update python encoding
	pyv = run("""python -c 'import sys; print "%s.%s" % (sys.version_info[0], sys.version_info[1])'""")
	sudo("""sed -i 's/encoding.[^!]*=.*\"ascii\"/encoding=\"utf8\"/' %s/lib/python%s/site.py""" % (venv, pyv) )

	update_code(HOME_DIR, remote_home_dir)


def update_code(plocal, premote):
	local('tar -cvf %s/app.tar %s/' % (TMP_PATH, plocal))
	local('gzip -f %s/app.tar' % (TMP_PATH))
	put('%s/app.tar.gz' % (TMP_PATH), premote, use_sudo=True)
	sudo('gunzip %s/app.tar.gz' % (premote))
	sudo('tar -xvf %s/app.tar %s' % (premote, premote))


# Test Functions
################

def what_is_my_name():
	run('whoami')

def what_is_sudos_name():
	sudo('whoami')


