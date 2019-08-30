# FairyRosine

python manage.py runserver_plus --cert testcert 0.0.0.0:8000


daphne -e "ssl:8001:privateKey=myselfsigned.key:certKey=myselfsigned.cer" vef.asgi:application


##firefox flags:
**full-screen-api.allow-trusted-requests-only** - для разрешение выполнения `document.documentElement.requestFullscreen().then(() => ...`