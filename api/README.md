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

## Technical notes

- Authentication uses `rest_framework_simplejwt`.
- The logout endpoint requires `rest_framework_simplejwt.token_blacklist` in `INSTALLED_APPS`.
- The app stores agent-specific metadata in `AgentProfile`, linked to `Profile` via `OneToOneField`.
- `Profile` links to Django `User` via `user` field.
- `AgentProfile` uses JSON fields for lists like `languages_spoken`, `service_areas`, and `specialties`.
- `CustomTokenObtainPairSerializer` injects `role` and `username` claims into the JWT payload.

## Admin registration

The `Profile` and `AgentProfile` models are registered in the Django admin.

## CORS support

CORS settings are configured in `core/settings.py` using `django-cors-headers`.

## Running locally

Start the Django server from the `api` folder:

```bash
py manage.py runserver
```

Then use the JSON endpoints under `/api/auth/`.
