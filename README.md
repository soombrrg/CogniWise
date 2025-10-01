# CogniWise
**CogniWise** - Full-stack platform for selling online courses, featuring integrated payment system *YooMoney*. 

**Tech Stack**: 
- **Backend**: Django, PostgreSQL, Redis;
- **Frontend**: HTMX, TailwindCSS, AlpineJS;
- **Storage**: MinIO (S3-compatible) for static and media.

## How to run
### Prerequisites
- Docker and Docker Compose;
- Python 3.13+, UV;
- Make

### App 
Step-by-step:
- `cp .env.example src/.env`;
- `make deps`
- `compose up` - for db, cache, s3 containers running
- `make prep` - migrations
- `make up`

### App in Docker
When using **django-app** as **docker** container:
- `cp .env.docker_example src/.env`;
- `make build`
- In docker-compose uncomment **web** and **nginx** sections.
- `compose up`

### S3
S3 should contain in static folder (local-static):
- *covers/default_cover* (for courses)
- *avatars/default_avatar* (for users).
- *favicon.ico* (optional).

### Make commands
Commands:
- `make deps` - install/sync dependencies;
- `make lint` - run **black, isort, mypy, flake8**;
- `make test` - run **pytest** tests;
- `make prep` - migrations;
- `make build` - build docker image;
- `make up` - quick up server;
- `make up-prod` - up server with static collection and migrations;

## Development
### Debug Toolbar (if in docker)
If **django-app** running as **docker** container. 

To enable Debug Toolbar uncomment next section in *settings.py*:
```python
DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK": lambda request: True,
    "RENDER_PANELS": True,
}
```

### Nginx (if in docker)
If **Nginx** and **django-app** running as **docker** containers.

Use *local* ip (*192.168.100.xx*) to access django-app and s3:
- `/` - django app.
- `/s3/ui/` - minio **ui** interface;
- `/s3/api/` - minio **api** interface;

