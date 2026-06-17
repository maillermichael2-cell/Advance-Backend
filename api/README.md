# API Security App Documentation

## Overview

The `security` app provides authentication and user registration for both individual users and estate agents.

It includes:
- JWT login using `djangorestframework-simplejwt`
- Registration with role-based agent metadata
- Refresh token support
- Logout via token blacklisting
- User `Profile` and agent-specific `AgentProfile` models

## Models

### Profile

Fields:
- `user`: One-to-one link to Django `User`
- `role`: `ESTATE AGENT` or `INDIVIDUAL`
- `phone_number`: optional contact number

### AgentProfile

Fields:
- `profile`: One-to-one link to `Profile`
- `license_number`: required for agents
- `license_state_region`
- `agency_name`
- `agency_office_address`
- `job_title`
- `languages_spoken` (JSON list)
- `service_areas` (JSON list)
- `specialties` (JSON list)
- `preferred_lead_routing`: `BOTH`, `BUYER`, or `SELLER`
- `years_of_experience`

## Endpoints

All endpoints are mounted under `/api/` and the security app paths are defined in `api/security/urls.py`.

### POST `/api/auth/register/`

Registers a new user and creates the required `Profile` and optional `AgentProfile`.

#### Accepted JSON payloads

You can send either a nested `user` object or top-level `username`, `email`, and `password` fields.

##### Nested user example

```json
{
  "user": {
    "username": "john.smith",
    "email": "john.smith@realty.com",
    "password": "StrongPassword123!"
  },
  "role": "ESTATE AGENT",
  "phone_number": "+15551234567",
  "agent_meta": {
    "license_number": "RE-889211-CA",
    "license_state_region": "California",
    "agency_name": "Vanguard Properties",
    "agency_office_address": "456 Market St, San Francisco, CA",
    "job_title": "Senior Broker",
    "languages_spoken": ["English", "French"],
    "service_areas": ["San Francisco", "Oakland"],
    "specialties": ["Luxury Real Estate", "Commercial"],
    "preferred_lead_routing": "BOTH",
    "years_of_experience": 8
  }
}
```

##### Top-level user payload example

```json
{
  "username": "john.smith",
  "email": "john.smith@realty.com",
  "password": "StrongPassword123!",
  "role": "INDIVIDUAL",
  "phone_number": "+15551234567"
}
```

#### Notes
- `role` is required.
- If `role` is `ESTATE AGENT`, `agent_meta` is required.
- `agent_meta.license_number` is required for agents.

#### Response

Success response returns a confirmation payload with created user info:

```json
{
  "message": "User registered successfully.",
  "user": {
    "username": "john.smith",
    "email": "john.smith@realty.com"
  },
  "role": "ESTATE AGENT",
  "phone_number": "+15551234567",
  "agent_meta": {
    "license_number": "RE-889211-CA",
    "license_state_region": "California",
    "agency_name": "Vanguard Properties",
    "agency_office_address": "456 Market St, San Francisco, CA",
    "job_title": "Senior Broker",
    "languages_spoken": ["English", "French"],
    "service_areas": ["San Francisco", "Oakland"],
    "specialties": ["Luxury Real Estate", "Commercial"],
    "preferred_lead_routing": "BOTH",
    "years_of_experience": 8
  }
}
```

### POST `/api/auth/login/`

Authenticates a user and returns JWT tokens.

#### Request payload

```json
{
  "username": "john.smith",
  "password": "StrongPassword123!"
}
```

#### Response

The login endpoint returns an access token and refresh token. The access token includes custom claims for `role` and `username`.

Example:

```json
{
  "refresh": "<refresh_token>",
  "access": "<access_token>"
}
```

### POST `/api/auth/token/refresh/`

Refreshes the access token using a valid refresh token.

#### Request payload

```json
{
  "refresh": "<refresh_token>"
}
```

#### Response

```json
{
  "access": "<new_access_token>"
}
```

### POST `/api/auth/logout/`

Blacklists a refresh token using SimpleJWT's built-in blacklist view.

#### Request payload

```json
{
  "refresh": "<refresh_token>"
}
```

#### Response

```json
{
  "detail": "Token blacklisted successfully."
}
```

## API Documentation (Swagger / OpenAPI)

The API includes auto-generated interactive documentation powered by **drf-spectacular**.

### Accessing the Documentation

Once the server is running, visit:

- **Swagger UI (Interactive):** `http://127.0.0.1:3030/api/docs/`
- **ReDoc (Alternative UI):** `http://127.0.0.1:3030/api/redoc/`
- **OpenAPI Schema (JSON):** `http://127.0.0.1:3030/api/schema/`

The Swagger UI allows you to:
- View all available endpoints
- See request/response schemas
- Test endpoints directly with the "Try it out" feature
- Authorize with JWT tokens via the "Authorize" button

### JWT Authorization in Swagger

1. Register and login to get a JWT access token
2. Click the **Authorize** button (top-right in Swagger UI)
3. Enter `Bearer <your_access_token>` in the authorization modal
4. All subsequent requests will include the token

## Properties App Documentation

The `properties` app provides a complete real estate property management API with image uploads, favorites, and category management.

### Models

#### PropertyCategory
Fields:
- `name`: Category name (e.g., "Residential", "Commercial")
- `slug`: URL-friendly identifier

#### Property
Fields:
- `title`: Property name/title
- `property_address`: Full address
- `description`: Detailed property description
- `price`: Decimal price
- `category`: ForeignKey to `PropertyCategory`
- `owner`: ForeignKey to Django `User` (the creating agent)
- `status`: One of `AVAILABLE`, `PENDING`, `UNDER_OFFER`, `SOLD`
- `created_at`: Timestamp
- **Documentation Status:** `registered_survey`, `deed_of_assignment`, `building_plan_approval`, `c_of_o`, `governors_consent` (all optional)
- **Land & Building Features:** `land_size`, `sq_meters`, `unit_size`, `construction_status`, `number_of_bedrooms`, `number_of_bathrooms`

#### PropertyImage
Fields:
- `property`: ForeignKey to `Property`
- `image`: Image file upload
- `uploaded_at`: Timestamp
- `order`: Display order (0 = first)

#### Favorite
Fields:
- `user`: ForeignKey to Django `User`
- `property`: ForeignKey to `Property`
- `created_at`: Timestamp
- **Constraint:** Unique together (`user`, `property`)

### Properties Endpoints

All property endpoints require authentication. Base path: `/api/`

#### Property Categories

- **GET** `/api/properties/categories/` - List all categories (public read)
- **POST** `/api/properties/categories/` - Create category (authenticated)
- **GET** `/api/properties/categories/<id>/` - Retrieve category (public read)
- **PUT** `/api/properties/categories/<id>/` - Update category (authenticated)
- **DELETE** `/api/properties/categories/<id>/` - Delete category (authenticated)

#### Properties

- **GET** `/api/properties/` - List properties
  - **For agents:** Returns only properties they own
  - **For individuals/public:** Returns all properties
- **POST** `/api/properties/` - Create property (agent-only)
- **GET** `/api/properties/<id>/` - Retrieve property (agent sees own only, others see all)
- **PUT** `/api/properties/<id>/` - Update property (owner-only)
- **PATCH** `/api/properties/<id>/` - Partial update (owner-only)
- **DELETE** `/api/properties/<id>/` - Delete property (owner-only)

#### Favorites

- **GET** `/api/favorites/` - List current user's favorites (authenticated)
- **POST** `/api/favorites/` - Add property to favorites (authenticated)
- **DELETE** `/api/favorites/<id>/` - Remove from favorites (authenticated)

#### Property Images

- **GET** `/api/property-images/` - List images (supports `?property_id=<id>` filter)
- **POST** `/api/property-images/` - Upload image (authenticated)
- **GET** `/api/property-images/<id>/` - Retrieve image
- **PUT** `/api/property-images/<id>/` - Update image order (authenticated)
- **DELETE** `/api/property-images/<id>/` - Delete image (authenticated)

### Permission Model

The properties app enforces strict ownership and role-based access control:

#### Estate Agents
- ✅ Can **create** properties
- ✅ Can **view, update, delete** ONLY their own properties
- ❌ Cannot see properties owned by other agents
- ✅ Can add/remove properties from favorites

#### Individuals
- ❌ Cannot create properties
- ✅ Can **view all** properties
- ❌ Cannot update or delete any properties
- ✅ Can add/remove properties from favorites

#### Anonymous Users
- ✅ Can view public property endpoints (read-only)
- ❌ Cannot modify anything
- ❌ Cannot access favorites

### Example: Create a Property (Agent)

**Step 1: Register as an agent**
```bash
curl -X POST http://127.0.0.1:3030/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "agent.smith",
    "email": "agent.smith@realty.com",
    "password": "SecurePassword123!",
    "role": "ESTATE AGENT",
    "phone_number": "+15551234567",
    "agent_meta": {
      "license_number": "RE-12345",
      "agency_name": "Prime Properties"
    }
  }'
```

**Step 2: Login to get JWT token**
```bash
curl -X POST http://127.0.0.1:3030/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "agent.smith",
    "password": "SecurePassword123!"
  }'
```

Response:
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Step 3: Create a property**
```bash
curl -X POST http://127.0.0.1:3030/api/properties/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..." \
  -d '{
    "title": "Luxury Downtown Penthouse",
    "property_address": "123 Main St, Downtown",
    "description": "Beautiful 3-bedroom penthouse with city views",
    "price": "2500000.00",
    "category": 1,
    "status": "AVAILABLE",
    "number_of_bedrooms": 3,
    "number_of_bathrooms": 2,
    "sq_meters": 250.5
  }'
```

### Technical Implementation

**Custom Permission Class:** `IsAgentCreatorOrOwner`
- Located in `properties/permissions.py`
- Enforces role-based CRUD restrictions
- Agents automatically become property owners on creation
- Only property owners can modify/delete their properties

**Querysets:** All property views use optimized querysets with:
- `select_related('category', 'owner')` - Reduces database queries for ForeignKey fields
- `prefetch_related('images')` - Efficient loading of related images
- Agent filtering in `get_queryset()` - Returns filtered results based on user role

## Technical notes

- Authentication uses `rest_framework_simplejwt`.
- The logout endpoint requires `rest_framework_simplejwt.token_blacklist` in `INSTALLED_APPS`.
- The app stores agent-specific metadata in `AgentProfile`, linked to `Profile` via `OneToOneField`.
- `Profile` links to Django `User` via `user` field.
- `AgentProfile` uses JSON fields for lists like `languages_spoken`, `service_areas`, and `specialties`.
- `CustomTokenObtainPairSerializer` injects `role` and `username` claims into the JWT payload.
- API documentation is provided by `drf-spectacular` (OpenAPI 3.0 schema generation).
- Property visibility is controlled via custom permission class and queryset filtering.

## Admin registration

The `Profile` and `AgentProfile` models are registered in the Django admin.

## CORS support

CORS settings are configured in `core/settings.py` using `django-cors-headers`.

## Docker Setup (Recommended for Development)

The project includes complete Docker configuration for easy setup and deployment.

### Quick Start with Docker

1. **Prerequisites:** Docker and Docker Compose installed

2. **Build and Run:**
   ```bash
   cd /path/to/apigitfolder
   docker-compose up --build
   ```

3. **Access the API:**
   - API: http://localhost:8000/api/
   - Swagger Docs: http://localhost:8000/api/docs/
   - Admin Panel: http://localhost:8000/admin/ (login: admin/admin123)
   - ReDoc: http://localhost:8000/api/redoc/

4. **Stop Containers:**
   ```bash
   docker-compose down
   ```

### What Docker Provides

- ✅ Isolated Python environment (no virtual env needed on host)
- ✅ PostgreSQL database pre-configured
- ✅ Automatic migrations on startup
- ✅ Auto-created superuser (admin:admin123)
- ✅ Hot-reload for code changes
- ✅ All environment variables pre-configured

### Docker Architecture

The setup includes two containers:
1. **Django API** (port 8000) - Runs your application
2. **PostgreSQL** (port 5432) - Database server

See [DOCKER.md](../DOCKER.md) for comprehensive Docker documentation including:
- Advanced Docker commands
- Troubleshooting
- Production deployment
- Performance optimization

## Running locally

Start the Django server from the `api` folder:

```bash
py manage.py runserver
```

Then use the JSON endpoints under `/api/auth/`.



### 💾 Database Setup (Supabase Postgres)

#### 1. Enable Database Extensions
The properties application uses performance-optimized search indexes (`GinIndex`). You must activate the trigram matching operators directly inside your online Supabase instance before executing migrations:
1. Navigate to your **Supabase Dashboard**.
2. Go to **Database** (left sidebar) ➡️ **Extensions**.
3. Search for **`pg_trgm`** and toggle it **ON**.

#### 2. Get Your Connection String
1. In your Supabase Dashboard, go to **Project Settings** ➡️ **Database**.
2. Scroll down to the **Connection string** section and select **Direct**.
3. Choose the **Transaction Pooler** toggle option.
4. Copy the URI string. Ensure the string uses port **`6543`** to route through the connection pooler safely.

#### 3. Configure Local Environment (`.env`)
Create a `.env` file in your root directory (`/api/`) right next to `manage.py` and paste your connection string. 

> ⚠️ **CRITICAL STRING ENCODING RULE:** If your Supabase password contains special characters (e.g., `!`, `@`, `:`, `#`), you **MUST** URL-encode them manually (`!` ➡️ `%21`, `@` ➡️ `%40`, `:` ➡️ `%3A`). Otherwise, Python's URL parser will throw a routing `ValueError`.

```text
DATABASE_URL=postgresql://postgres:YourEncodedPassword%21@://supabase.com
```

#### 4. Project Configuration (`core/settings.py`)
Ensure your core application routes traffic through `django-environ` and `django.contrib.postgres` by verifying these settings properties are defined:

```python
INSTALLED_APPS = [
    # ...
    'django.contrib.postgres',  # Required for GinIndex & Trigram operations
    # ...
]

# Database routing engine parsing the URL
DATABASE_URL = env('DATABASE_URL', default=None)

if DATABASE_URL:
    url = urllib.parse.urlparse(DATABASE_URL)
    db_name = url.path[1:].split('?')[0] if '?' in url.path else url.path[1:]

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': db_name,
            'USER': url.username,
            'PASSWORD': url.password,
            'HOST': url.hostname,
            'PORT': url.port or 5432,
            'CONN_MAX_AGE': 600,  # Persists database connections up to 10 minutes
            'OPTIONS': {
                'sslmode': 'require',
            },
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
```

#### 5. Execute Schema Sync
Run the migration command in your local terminal to inject all authentication, account profile, and real estate listing tables directly into your production Supabase cluster:

```bash
python manage.py migrate
```
