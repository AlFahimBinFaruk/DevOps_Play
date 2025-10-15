1. Run the server

```cmd
docker compose up --build

- Run with scaling
docker compose up --scale fastapi_app=3
```

2. Run the seeder(from your project root,outside src dir)

```cmd
python3 -m src.scripts.seeder all
```

3. Test Scaling

```cmd
python3 test-load-balancer.py
```

4. Run migration

```cmd
alembic init migrations
alembic revision --autogenerate -m "some comment"
alembic upgrade head
```

### TODO

- [x] Setup Postgresql db with docker
- [x] How to generate migration file
- [x] How to create seeder script
- [x] Auth with JWT
- [x] Middleware(dependency injection)
- [x] Proper structure
- [x] Reload every time something changes in file in docker version
- [x] issue ⇒ Cant find db at first => solved with restart
- [x] Configured load balancer with nginx.
- [x] Configured prometheous,grafana,Loki.
