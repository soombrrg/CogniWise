In development just send .env file in src directory

When using docker and docker compose 
Change how  env used

In settings.py write
```
env = environ.FileAwareEnv()
```
and delete
```
environ.Env.read_env(BASE_DIR / ".env")
```

Then docker-compose.yml should contain:

```
secrets:
  secret_key:
    external: true

services:
  app:
    secrets:
      - secret_key
    environment:
      - SECRET_KEY_FILE=/run/secrets/secret_key
```



