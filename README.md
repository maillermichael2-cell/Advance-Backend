
| Phase | Week | Core Topic / Focus | Actionable SaaS Task | Key Tech / Tools |
| :--- | :--- | :--- | :--- | :--- |
| **Phase 1: API Mastery** | **Week 1** | Serializers & ViewSets | Remove HTML templates; convert property CRUD to JSON endpoints. | `djangorestframework` |
| | **Week 2** | Relations & Filtering | Add agent-to-property relationships, pagination, and location filters. | DRF Filters |
| | **Week 3** | Token Authentication | Secure the API with login, logout, and custom agent permissions. | `django-rest-framework-simplejwt` |
| | **Week 4** | Documentation & Testing | Auto-generate API docs and write basic endpoint integration tests. | `drf-spectacular` |
| **Phase 2: FastAPI & Async** | **Week 5** | FastAPI & Pydantic | Learn type hinting; build a microservice for property leads/forms. | `fastapi`, `pydantic` |
| | **Week 6** | Async Concepts | Master `async`/`await`; learn when to use async vs sync paths. | Python AsyncIO |
| | **Week 7** | Async Database Connections| Connect FastAPI to PostgreSQL using an asynchronous ORM layer. | `SQLAlchemy` or `Tortoise ORM` |
| | **Week 8** | Real-Time WebSockets | Build a live chat microservice for buyers and agents to message. | FastAPI WebSockets |
| **Phase 3: System Design** | **Week 9** | Indexing & Caching | Index frequent query fields; cache the homepage property listings. | PostgreSQL Indexes, `redis` |
| | **Week 10** | Background Task Queues | Move slow actions (image resizing, email receipts) out of request cycles. | `celery` or `huey` |
| | **Week 11** | Containerization | Bundle API, DB, and Redis to launch locally with one terminal command. | `docker`, `docker-compose` |
| | **Week 12** | Production & Monitoring | Deploy your multi-service app and set up live error logging. | Render/Neon, `sentry-sdk` |
