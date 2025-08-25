1. Run the server
```cmd
docker compose up --build
```
2. Run the seeder(from your project root(outside src dir))
```cmd
python3 -m src.scripts.seeder all
```

### TODO
- [x]  Setup Postgresql db with docker
- [x]  How to generate migration file
- [x]  How to create seeder script
- [x]  Auth with JWT
- [x]  Middleware
- [x]  Proper structure
- [x]  Reload every time something changes in file in docker version
- [x]  issue ⇒ Cant find db at first