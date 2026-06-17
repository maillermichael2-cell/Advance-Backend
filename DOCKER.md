# Docker Quick Start

## Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+

For Windows users using Docker Desktop, both are included.

## Building and Running

### Development with Docker Compose

The easiest way to run the entire stack (Django API + PostgreSQL):

```bash
cd /path/to/apigitfolder
docker-compose up --build
```

This will:
1. Build the Docker image for the Django API
2. Start a PostgreSQL database container
3. Run migrations automatically
4. Create a superuser (`admin:admin123`)
5. Start the Django development server on port 8000

**Access the API:**
- API: http://localhost:8000/api/
- Swagger Docs: http://localhost:8000/api/docs/
- Admin Panel: http://localhost:8000/admin/
- ReDoc: http://localhost:8000/api/redoc/

### Running Subsequent Times

After the initial build, you can simply use:

```bash
docker-compose up
```

To rebuild after code changes:

```bash
docker-compose up --build
```

### Stopping Containers

```bash
docker-compose down
```

To remove volumes (database data):

```bash
docker-compose down -v
```

## Docker Architecture

```
┌─────────────────────────────────────┐
│      Docker Compose Network         │
├─────────────────────────────────────┤
│                                     │
│  ┌─────────────┐  ┌──────────────┐ │
│  │   Django    │  │  PostgreSQL  │ │
│  │   API Web   │  │   Database   │ │
│  │ (port 8000) │  │ (port 5432)  │ │
│  │             │  │              │ │
│  │ - Migrations│  │ realty_db    │ │
│  │ - Static    │  │              │ │
│  │ - Swagger   │  │ postgres_data│ │
│  └──────┬──────┘  └──────┬───────┘ │
│         │                │         │
│         └────────┬───────┘         │
│                  │                 │
└──────────────────┼─────────────────┘
                   │
            ┌──────┴──────┐
            │   Host OS   │
            │ localhost:  │
            │ :8000 (API) │
            │ :5432 (DB)  │
            └─────────────┘
```

## Services

### Web Service (`web`)

**Image:** Custom built from `Dockerfile`  
**Container Name:** `realty_api_web`  
**Port:** 8000  
**Volumes:** `./api:/app` (live reload during development)

**Environment Variables:**
- `DEBUG=True` (set to False in production)
- `SECRET_KEY=...` (change in production)
- `DATABASE_URL=postgresql://realty_user:realty_password@db:5432/realty_db`
- `ALLOWED_HOSTS=localhost,127.0.0.1,web`

**Entrypoint Script (`entrypoint.sh`):**
1. Waits for database to be ready
2. Runs `python manage.py migrate`
3. Creates superuser if it doesn't exist
4. Collects static files
5. Starts Django development server

### Database Service (`db`)

**Image:** postgres:15-alpine  
**Container Name:** `realty_api_db`  
**Port:** 5432  
**Volume:** `postgres_data` (persistent storage)

**Credentials:**
- User: `realty_user`
- Password: `realty_password`
- Database: `realty_db`

**Health Check:** Verifies PostgreSQL is accepting connections

## File Structure

```
apigitfolder/
├── Dockerfile              # Django app container definition
├── docker-compose.yml      # Multi-container orchestration
├── entrypoint.sh          # Container startup script
├── .dockerignore           # Files excluded from Docker build
│
├── api/
│   ├── manage.py
│   ├── requirements.txt    # Python dependencies
│   ├── .env.docker        # Docker environment config
│   ├── core/
│   ├── properties/
│   ├── security/
│   └── db.sqlite3         # SQLite database (only for local dev without Docker)
│
└── README.md
```

## Common Docker Commands

### View Logs

```bash
# All services
docker-compose logs

# Specific service
docker-compose logs web
docker-compose logs db

# Follow logs in real-time
docker-compose logs -f web
```

### Execute Commands in Container

```bash
# Run Django management command
docker-compose exec web python manage.py createsuperuser

# Open Django shell
docker-compose exec web python manage.py shell

# Access database
docker-compose exec db psql -U realty_user -d realty_db
```

### Rebuild Without Cache

```bash
docker-compose build --no-cache
docker-compose up
```

### Remove Unused Images/Containers

```bash
docker system prune -a
```

## Troubleshooting

### Database Connection Refused

If you get connection errors:

1. Check database status:
   ```bash
   docker-compose ps
   ```

2. View database logs:
   ```bash
   docker-compose logs db
   ```

3. Verify the health check passed:
   ```bash
   docker-compose exec db pg_isready -U realty_user -d realty_db
   ```

### Port Already in Use

If port 8000 or 5432 is already in use:

**Option 1:** Stop conflicting services
```bash
docker-compose down
```

**Option 2:** Change port mappings in `docker-compose.yml`
```yaml
ports:
  - "8001:8000"  # Maps host:8001 to container:8000
  - "5433:5432"  # Maps host:5433 to container:5432
```

### Static Files Not Loading

```bash
docker-compose exec web python manage.py collectstatic --noinput
```

### Need to Reset Database

```bash
docker-compose down -v
docker-compose up --build
```

## Production Deployment

For production deployment, use:

1. **Gunicorn** instead of Django development server
2. **Nginx** as reverse proxy
3. **Environment-specific** settings
4. **Managed PostgreSQL** service (e.g., AWS RDS, Supabase)
5. **Docker Registry** for image storage

Example production `docker-compose.yml`:

```yaml
services:
  web:
    image: your-registry/realty-api:latest
    environment:
      DEBUG: "False"
      SECRET_KEY: ${SECRET_KEY}
      DATABASE_URL: ${DATABASE_URL}
    command: gunicorn core.wsgi:application --bind 0.0.0.0:8000
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/schema/"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - web
```

## Performance Tips

1. **Use Alpine images** for smaller image sizes
2. **Multi-stage builds** for production (not shown here)
3. **Layer caching** - order Dockerfile commands by change frequency
4. **Volume mounts** only for development (use COPY for production)
5. **Resource limits** - Add `mem_limit` and `cpu_shares` in compose file

## Security Considerations

⚠️ **IMPORTANT FOR PRODUCTION:**

1. Change `SECRET_KEY` in `docker-compose.yml`
2. Change default database credentials
3. Set `DEBUG=False` in production
4. Use environment files (`.env`) instead of hardcoding secrets
5. Enable SSL/TLS with Nginx
6. Use Docker secrets for sensitive data
7. Implement regular backups of `postgres_data` volume

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Django Docker Best Practices](https://docs.djangoproject.com/en/stable/topics/deploy/wsgi/django-gunicorn/)
- [PostgreSQL in Docker](https://hub.docker.com/_/postgres)
