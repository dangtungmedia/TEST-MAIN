$ virtualenv env
$ source env/bin/activate
$ pip3 install -r requirements.txt

$pip freeze > requirements.txt



< PROJECT ROOT >
    |
    | -- celeryworker
    |       |-- celery.py
    |       |-- celeryconfig.py
    |       |-- task.py
    | -- requirements.txt  
    | -- .env 
    | -- docker-compose.yml
    | -- Dockerfile