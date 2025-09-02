deps:
	uv sync

lint:
	isort src
	black src
	mypy src
	flake8 src

test:
	cd src && pytest

up:
	cd src && python manage.py runserver

up-prod:
	cd src
	python ./manage.py collectstatic --no-input
	python ./manage.py migrate
	uvicorn app.asgi:application --host 0.0.0.0 --port 8000

build:
	docker build -t test .


