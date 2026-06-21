
import os

from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site

GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')

site = Site.objects.get(id=1)

app, created = SocialApp.objects.get_or_create(
    provider='google',
    name='Google',
    defaults={
        'client_id': GOOGLE_CLIENT_ID,
        'secret': GOOGLE_CLIENT_SECRET,
    },
)


if not created:
    app.client_id = GOOGLE_CLIENT_ID
    app.secret = GOOGLE_CLIENT_SECRET
    app.save()

app.sites.add(site)

print('Created' if created else 'Updated', '-', app)