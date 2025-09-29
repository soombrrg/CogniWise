manage = uv run python src/manage.py

deps:
	uv sync

lint:
	black src
	mypy src
	flake8 src

test:
	cd src && uv run pytest

prep:
	$(manage) makemigrations
	$(manage) migrate

up:
	cd src && uvicorn app.asgi:application --host 0.0.0.0 --port 8000

up-prod:
	$(manage) collectstatic --no-input
	$(manage) migrate
	cd src && uvicorn app.asgi:application --host 0.0.0.0 --port 8000

build:
	docker build -t test .


