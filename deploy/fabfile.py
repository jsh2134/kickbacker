import os

from fabric.api import env, settings
from fabric.api import sudo, lcd, cd, run, local, put

import ec2

from kickbacker import app
from deploy.amazon_settings import MAIN_IP, aws_defaults

USER_HOME = '/home/jhull/'
HOME_DIR = app.config['HOME']
TMP_PATH = '/tmp/'
S3CFG_FILE = '.s3cfg'
S3CFG_FP = os.path.join(HOME_DIR, 'deploy', S3CFG_FILE)
KB_BUCKET = 's3://kickbacker/'
HOSTS = {	
			'web1' : { 'user':'ec2-user',
						'host': MAIN_IP,
						'key': os.path.join(USER_HOME, '.ssh', aws_defaults['keypair']['file'])
			},
		}

env.key_filename = HOSTS['web1']['key']

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
	
	remote_code_dir = os.path.join(remote_home_dir, 'kb')
	with settings(warn_only=True):
		sudo('mkdir %s' % remote_code_dir)

	# Install packages with yum
	sudo('yum install -y python-devel gcc nginx')

	# Install s3cmd tools
	#install_s3cmd(remote_home_dir)

	# Install pip
	sudo('curl -O http://pypi.python.org/packages/source/p/pip/pip-1.0.tar.gz')
	run('tar xvfz pip-1.0.tar.gz')
	sudo('cd pip-1.0 && python setup.py install')

	#run('echo $PYTHONPATH')

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
	
	# Install Nginx Config
	put('nginx.conf', '/etc/nginx/nginx.conf', use_sudo=True)

	# Install Supervisor Config
	sudo('mkdir %s/etc/' % venv)
	put('supervisord.conf', '%s/etc/supervisord.conf' % venv, use_sudo=True)

	# Update python encoding
	pyv = run("""python -c 'import sys; print "%s.%s" % (sys.version_info[0], sys.version_info[1])'""")
	sudo("""sed -i 's/encoding.[^!]*=.*\"ascii\"/encoding=\"utf8\"/' %s/lib/python%s/site.py""" % (venv, pyv) )

	update_code(HOME_DIR, remote_code_dir)

	# Install Redis
	install_redis()

	start_app(remote_code_dir)

def start_app(code_dir):
	# start nginx
	sudo('service nginx start')

	# start supervisor
	sudo('/home/kickbacker/kickbacker-env/bin/supervisord', pty=True)
	sudo('supervisorctl start redis celery kickbacker')

	# start redis
	#sudo("service redis start")

	# start celery
	#with cd(os.path.join(code_dir,'kickabacker','celery_queue')):
	#	run('celery -A tasks worker --loglevel=info')

	# start app
	#run('nohup python %s/handler.py > %s/app_log.log &' % (code_dir, code_dir), pty=False )


def update_code(plocal, premote):
	with lcd(plocal):
		local('git archive --format=tar.gz --output %s HEAD' % os.path.join(TMP_PATH, 'app.tar.gz'))
	put( os.path.join(TMP_PATH,'app.tar.gz'), os.path.join(premote, 'app.tar.gz'), use_sudo=True)
	sudo('gunzip %s' % os.path.join(premote, 'app.tar.gz'))
	with cd(premote):
		sudo('tar -xvf %s' % os.path.join(premote, 'app.tar'))

def install_redis():

	with settings(warn_only=True):
		sudo('useradd redis', pty=True)
		sudo('mkdir %s' % os.path.join('var','run','redis'), pty=True)
		sudo('mkdir %s' % os.path.join('var','lib','redis'), pty=True)
		sudo('mkdir %s' % os.path.join('var','log','redis'), pty=True)
		sudo('mkdir %s' % os.path.join('etc','redis'), pty=True)
		sudo('chown redis:redis /var/log/redis /var/lib/redis /var/run/redis')

	put('redis/redis.conf', '/etc/redis/redis.conf', use_sudo=True)
	put('redis/redis.init', '/etc/rc.d/init.d/redis', use_sudo=True)

	sudo('wget http://download.redis.io/redis-stable.tar.gz', pty=True)
	sudo('tar xvzf redis-stable.tar.gz', pty=True)
	with cd('redis-stable'):
		sudo('make', pty=True)
		sudo('make install', pty=True)
		sudo('cp redis-server /usr/local/bin/')
		sudo('cp redis-cli /usr/local/bin/')

	sudo('service redis start', pty=True)



