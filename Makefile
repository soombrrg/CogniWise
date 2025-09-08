deps:
	uv sync

lint:
	black src
	mypy src
	flake8 src

prep:
	cd src && python manage.py makemigrations
	cd src && python manage.py migrate

test:
	cd src && pytest

up:
	cd src && uvicorn app.asgi:application --host 0.0.0.0 --port 8000

up-prod:
	cd src && python manage.py collectstatic --no-input
	cd src && python manage.py migrate
	cd src && uvicorn app.asgi:application --host 0.0.0.0 --port 8000

build:
	docker build -t test .


