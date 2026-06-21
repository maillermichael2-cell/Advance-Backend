# Google OAuth — Usage Guide

allauth handles the Google login itself (redirect, consent, code exchange,
user creation) and sets a Django **session**. Since this is an API, a custom
view converts that session into JWTs once the user has a complete profile
(individual vs. estate agent — Google doesn't tell us which).

## Endpoints

| Method | Path | Auth | Purpose |
|---|---|---|---|
| GET | `/accounts/google/login/` | none | Starts Google login (allauth) |
| GET | `/api/auth/google/token/` | session | Checks profile, issues JWTs or redirects to onboarding |
| POST | `/api/auth/completeprofile/` | session | Submits role + agent fields (if agent), creates `Profile`/`AgentProfile`, returns JWTs |

## How to test

**1. Log in (real browser required — Google's screen can't be hit from an API tool)**
```
http://localhost:8000/accounts/google/login/
```
Log in with a test account, consent.

**2. Expect a redirect to your frontend's onboarding page** (will fail to load if no frontend is running — that's fine, the session cookie is now set on `localhost:8000`).

**3. In the same browser tab**, go to:
```
http://localhost:8000/api/auth/completeprofile/
```
Use the DRF browsable API's **Raw data** tab (`application/json`) and POST one of:

Individual:
```json
{ "role": "INDIVIDUAL", "phone_number": "08012345678" }
```

Estate agent (`license_number` required):
```json
{
  "role": "ESTATE AGENT",
  "license_number": "TEST-001",
  "agency_name": "Test Realty"
}
```

You'll get back:
```json
{ "access": "...", "refresh": "..." }
```

**4. Use the access token everywhere else** (Thunder Client, Postman, etc.):
```
Authorization: Bearer <access token>
```

## Posting a property with the token

Once you have an `access` token (and your user has the `ESTATE AGENT` role,
if that's required by your permissions), use it to create a property:

```
POST http://localhost:8000/api/properties/
Authorization: Bearer <access token>
Content-Type: application/json
```

Body:
```json
{
    "title": "3 Bedroom Bungalow on 600sqm Land",
    "property_address": "12 Admiralty Way, Lekki Phase 1, Lagos",
    "description": "A beautifully finished 3-bedroom bungalow on a quiet, tarred street in Lekki Phase 1. The property sits on a dry, fenced 600sqm plot with ample parking space.",
    "price": "85000000.00",
    "category": 1,
    "status": "AVAILABLE",
    "registered_survey": "AVAILABLE",
    "deed_of_assignment": "AVAILABLE",
    "building_plan_approval": "AVAILABLE",
    "c_of_o": "NOT_AVAILABLE",
    "governors_consent": "NOT_AVAILABLE",
    "land_size": "600 sqm",
    "sq_meters": "600.00",
    "unit_size": "220 sqm",
    "construction_status": "COMPLETED",
    "number_of_bedrooms": 3,
    "number_of_bathrooms": 3
}
```

`"category"` must be an existing `PropertyCategory` ID — check available
categories first if unsure:
```
GET http://localhost:8000/api/properties/categories/
Authorization: Bearer <access token>
```

## Notes

- Steps 1–3 must happen in the **same browser tab** — the session cookie doesn't carry over to Thunder Client/Postman, which keep separate cookie jars. Either finish onboarding in the browser, or copy the `sessionid` cookie into your API client's headers.
- To re-test the new-user flow, delete the test user's profile:
```python
from django.contrib.auth.models import User
u = User.objects.get(email='your-test-email@gmail.com')
u.profile.delete()
```
- Google OAuth credentials live in the DB (`SocialApp`), not in `settings.py`. Registered redirect URI in Google Cloud Console must be `http://localhost:8000/accounts/google/login/callback/`, and you must use `localhost` consistently (not `127.0.0.1`) to avoid `redirect_uri_mismatch`.