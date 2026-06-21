# Google OAuth Authentication — Setup & Testing Guide

This document explains how Google OAuth login is wired into this Django API
using `django-allauth` + `djangorestframework-simplejwt`, and how to test the
full flow including the agent vs. individual onboarding branch.

---

## 1. Overview

allauth handles the actual Google OAuth dance (redirect to Google, consent,
code exchange, user creation) entirely on its own. It logs the user in via a
**Django session**. Since this is an API, we don't want session-based auth for
normal API calls — we want JWTs. So one custom view bridges the session into
JWT tokens once allauth is done.

On top of that, new users need to declare whether they're an **Individual**
or an **Estate Agent** before they get usable tokens, since Google doesn't
tell us that.

### High-level flow

```
1. User → GET /accounts/google/login/
2. allauth → redirects to Google's consent screen
3. User logs in / consents on Google
4. Google → redirects to /accounts/google/login/callback/ (allauth's own URL)
5. allauth → exchanges code, creates/links User, sets session cookie
6. allauth → redirects to LOGIN_REDIRECT_URL → /api/auth/google/issue-token/
7. GoogleIssueTokenView checks the user's Profile:
     - No Profile yet        → redirect to FRONTEND/auth/complete-profile
     - Agent, no AgentProfile → redirect to FRONTEND/auth/complete-agent-profile
     - Otherwise              → issue JWT tokens, redirect to FRONTEND/auth/callback
8. Frontend (or, for testing, you manually) POSTs to /api/auth/complete-profile/
   with role + agent fields if applicable → backend creates Profile/AgentProfile
   and returns JWT tokens directly as JSON.
```

---

## 2. Required settings

`settings.py` must include:

```python
INSTALLED_APPS = [
    ...
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
]

SITE_ID = 1

MIDDLEWARE = [
    ...
    'allauth.account.middleware.AccountMiddleware',
]

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
    }
}

LOGIN_REDIRECT_URL = '/api/auth/google/issue-token/'   # must start with '/'

FRONTEND_URL = 'http://localhost:3000'   # or your real frontend
```

Google credentials (`client_id` / `secret`) are stored in the database via a
`SocialApp` row, **not** in settings — see Section 4.

---

## 3. Google Cloud Console setup

1. Create a project at https://console.cloud.google.com/
2. **APIs & Services → OAuth consent screen**
   - User type: External
   - Add your test Google account under **Test users** (required while app is
     in "Testing" mode — anyone not listed will be blocked from logging in)
3. **APIs & Services → Credentials → + Create Credentials → OAuth client ID**
   - Application type: **Web application**
   - Authorized JavaScript origins: `http://localhost:8000`
   - Authorized redirect URIs: `http://localhost:8000/accounts/google/login/callback/`
   - Save the **Client ID** and **Client Secret**

⚠️ Use `localhost`, not `127.0.0.1`, consistently — Google treats them as
different origins and you'll get `redirect_uri_mismatch` if they don't match
exactly what's registered.

---

## 4. Register credentials in the database

Run once:

```bash
py manage.py shell
```

```python
from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site

site = Site.objects.get(id=1)
app, created = SocialApp.objects.get_or_create(
    provider='google',
    name='Google',
    defaults={'client_id': 'YOUR_CLIENT_ID', 'secret': 'YOUR_CLIENT_SECRET'},
)
app.sites.add(site)
```

Also make sure the `Site` domain is correct:

```python
site.domain = 'localhost:8000'
site.name = 'localhost'
site.save()
```

---

## 5. Endpoints

| Method | Path | Auth required | Purpose |
|---|---|---|---|
| GET | `/accounts/google/login/` | none | Starts the Google OAuth flow (allauth) |
| GET | `/accounts/google/login/callback/` | none | Google redirects here (allauth, code exchange) |
| GET | `/api/auth/google/issue-token/` | session cookie | Branches on profile completeness; issues JWTs or redirects to onboarding |
| POST | `/api/auth/complete-profile/` | session cookie | Submits role (+ agent fields if applicable); creates `Profile`/`AgentProfile`; returns JWT tokens as JSON |

### POST /api/auth/complete-profile/ — payload

**Individual:**
```json
{
  "role": "INDIVIDUAL",
  "phone_number": "08012345678"
}
```

**Estate agent** (`license_number` is required for this role):
```json
{
  "role": "ESTATE AGENT",
  "phone_number": "08012345678",
  "license_number": "TEST-001",
  "license_state_region": "Lagos",
  "agency_name": "Test Realty",
  "agency_office_address": "12 Admiralty Way, Lekki",
  "job_title": "Senior Agent",
  "languages_spoken": ["English", "Yoruba"],
  "service_areas": ["Lekki", "Ikoyi"],
  "specialties": ["Residential", "Land"],
  "preferred_lead_routing": "BOTH",
  "years_of_experience": 5
}
```

**Response (both cases):**
```json
{
  "access": "<jwt access token>",
  "refresh": "<jwt refresh token>"
}
```

---

## 6. How to test the full flow

### Step 1 — Start the Google login (real browser required)
```
http://localhost:8000/accounts/google/login/
```
Log in with the Google account you added as a test user. Consent.

You'll be redirected through allauth → `issue-token/` → (most likely, for a
new user) `http://localhost:3000/auth/complete-profile`. This will fail to
load since there's no frontend running — **that's expected**. What matters
is the session cookie is now set on `localhost:8000`.

### Step 2 — Complete the profile, in the same browser
Navigate to:
```
http://localhost:8000/api/auth/complete-profile/
```
This loads the DRF browsable API (it shares cookies with the page above
since both are on `localhost:8000`). Use the **Raw data** tab, content type
`application/json`, and paste one of the payloads from Section 5. Click
**POST**.

You should get back `{"access": "...", "refresh": "..."}` directly in the
response body.

### Step 3 — Use the access token in Thunder Client
```
GET http://localhost:8000/api/properties/
Authorization: Bearer <access token from step 2>
```

### Resetting a test user (to re-run the new-user flow)
```python
py manage.py shell
```
```python
from django.contrib.auth.models import User
u = User.objects.get(email='your-test-email@gmail.com')
u.profile.delete()   # also cascades AgentProfile if present
```

---

## 7. Common errors and fixes

| Error | Cause | Fix |
|---|---|---|
| `redirect_uri_mismatch` | Browser URL host doesn't match registered redirect URI exactly | Use `localhost`, not `127.0.0.1`, consistently; check trailing slash |
| `Page not found /accounts/profile/` | `LOGIN_REDIRECT_URL` not set or not picked up | Confirm it's in `settings.py` and starts with `/` |
| `404 .../callback/api/auth/...` | `LOGIN_REDIRECT_URL` missing leading slash | Must be `/api/auth/google/issue-token/`, not `api/auth/google/issue-token/` |
| `401 Authentication credentials were not provided` on `issue-token/` | View only had `JWTAuthentication`, no session support | Add `authentication_classes = [SessionAuthentication]` to the view |
| `Access blocked... invalid request` on Google's screen | Test account not added to consent screen test users | Add it under OAuth consent screen → Test users |
| Property creation blocked / wrong permissions | New Google user has no `Profile` yet | Must complete `/api/auth/complete-profile/` first |