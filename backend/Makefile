env:
	poetry env use 3.13
	poetry install

start-server:
	poetry run python manage.py runserver

start-celery:
	poetry run python -m celery -A Instanssi worker -l info --autoscale 2,1

migrate:
	poetry run python manage.py migrate

create-admin:
	poetry run python manage.py createsuperuser --username admin --email admin@invalid.inv --skip-checks

black:
	poetry run black .

isort:
	poetry run isort .

pytest:
	poetry run pytest

mypy:
	poetry run mypy -p Instanssi.api.v2

pytest-parallel:
	poetry run pytest -n $$((`nproc` / 2))

coverage:
	poetry run pytest --cov=Instanssi

django-check:
	poetry run python manage.py check

openapi:
	poetry run python manage.py spectacular --lang en --file openapi.yaml

format: black isort
check: black isort mypy pytest-parallel django-check
checks: check
