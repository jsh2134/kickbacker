sudo service mysqld start
sudo service redis start
python handler.py &
sudo celeryd --app=kickbacker.celery_queue.celery_queue.celery_server --loglevel=INFO
