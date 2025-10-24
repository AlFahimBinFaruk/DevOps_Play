I want to convert my current project into micro-service.
there will be mainly two services
1. user-management(fastapi,postgresql)
2. note-management(todo will be converted to notes)(fastapi,mongodb)


for current convinience i want to keep everything in the same repo.
but they should works as microservices.

req:
* i want to use jwt for validation(shared secrets)
* use pymongo for mongodb management.
* all the logging,monitoring,tracing will be used by a centralized service(we can call that log-service)-what do you think about this?
* every-serivce will have their own dockerfile,compose etc so that can work independently of each other(like micro-serivices should), but we can use shell script to run/stop etc all the services at once for convinience.

i want to use this project structure
```md
Note_Taker/
│
├── services/
│   ├── user-management/
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── .env.example
│   │   ├── alembic.ini
│   │   ├── alembic/
│   │   │   └── versions/
│   │   ├── src/
│   │   │   ├── __init__.py
│   │   │   ├── main.py
│   │   │   ├── core/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── config.py
│   │   │   │   ├── security.py          # JWT creation/validation
│   │   │   │   └── middleware.py        # Logging, metrics, auth
│   │   │   ├── db/
│   │   │   │   ├── __init__.py
│   │   │   │   └── database.py          # PostgreSQL connection
│   │   │   ├── user/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── models.py
│   │   │   │   ├── schemas.py
│   │   │   │   ├── services.py
│   │   │   │   └── views.py             # Auth, register, login, user CRUD
│   │   │   ├── scripts/
│   │   │   │   ├── __init__.py
│   │   │   │   └── seeder.py
│   │   │   └── observability/
│   │   │       ├── __init__.py
│   │   │       ├── tracing.py           # OpenTelemetry
│   │   │       ├── logging.py           # Loki handler
│   │   │       └── metrics.py           # Prometheus metrics
│   │   └── tests/
│   │       ├── __init__.py
│   │       ├── test_auth.py
│   │       └── test_users.py
│   │
│   └── note-service/
│       ├── Dockerfile
│       ├── requirements.txt
│       ├── .env.example
│       ├── src/
│       │   ├── __init__.py
│       │   ├── main.py
│       │   ├── core/
│       │   │   ├── __init__.py
│       │   │   ├── config.py
│       │   │   ├── security.py          # JWT validation (same secret as user service)
│       │   │   └── middleware.py        # Auth verification, logging, metrics
│       │   ├── db/
│       │   │   ├── __init__.py
│       │   │   └── database.py          # MongoDB connection
│       │   ├── note/
│       │   │   ├── __init__.py
│       │   │   ├── models.py            # Pydantic models (not SQLModel)
│       │   │   ├── schemas.py
│       │   │   ├── services.py
│       │   │   └── views.py             # Note CRUD endpoints
│       │   ├── scripts/
│       │   │   ├── __init__.py
│       │   │   └── seeder.py
│       │   └── observability/
│       │       ├── __init__.py
│       │       ├── tracing.py
│       │       ├── logging.py
│       │       └── metrics.py
│       └── tests/
│           ├── __init__.py
│           └── test_notes.py
│
├── infrastructure/
│   ├── nginx/
│   │   ├── nginx.conf                   # API Gateway configuration
│   │   └── Dockerfile (optional)
│   ├── observability/
│   │   ├── prometheus/
│   │   │   ├── prometheus.yml
│   │   │   └── alert-rules.yml
│   │   ├── grafana/
│   │   │   ├── grafana.yml
│   │   │   └── dashboards/
│   │   ├── loki/
│   │   │   └── loki.yml
│   │   ├── tempo/
│   │   │   └── tempo.yml
│   │   └── alertmanager/
│   │       └── alertmanager.yml
│   └── docker/
│       └── docker-compose.yml           # Main orchestration
│
├── scripts/
│   ├── start-all.sh                     # Start all services
│   ├── stop-all.sh                      # Stop all services
│   ├── build-all.sh                     # Build all Docker images
│   ├── start-user-service.sh            # Start only user service
│   ├── start-note-service.sh            # Start only note service
│   └── health-check.sh                  # Check all services health
│
├── shared/                              # Shared utilities (optional)
│   ├── __init__.py
│   └── jwt_utils.py                     # Shared JWT configuration
│
├── .env.example                         # Example environment variables
├── .gitignore
├── README.md
└── sonar-project.properties
```

ask me if you have any doubt before procedding.