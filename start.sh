sudo service redis start
ps -ef | grep handler.py | awk '{print $2}' | xargs kill
python handler.py &
celeryd --app=kickbacker.celery_queue.celery_queue.celery_server --loglevel=INFO
