mig:
	python manage.py makemigrations
	python manage.py migrate


fix:
	python manage.py loaddata categories products districts regions


admin:
	python manage.py createsuperuser

lang:
	python manage.py makemessages -l uz
	python manage.py makemessages -l en
	python manage.py makemessages -l ru

compile:
	python manage.py compilemessages

celery:
	celery -A root worker -l INFO

flower:
	celery -A root flower


beat:
	celery -A root beat -l info -S django


