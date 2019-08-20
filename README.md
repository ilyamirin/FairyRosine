# FairyRosine

python manage.py runserver_plus --cert testcert 0.0.0.0:8000


daphne -e "ssl:8001:privateKey=testcert.key:certKey=testcert.crt" vef.asgi:application