from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Profile(models.Model):
    ROLE_CHOICES = [
        ("ESTATE AGENT", 'Estate Agent'),
        ("INDIVIDUAL", 'Individual'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=100, choices=ROLE_CHOICES )
    phone_number = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f'{self.user.username} - {self.role}'

class AgentProfile(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name='agent_meta')
    license_number = models.CharField(max_length=50)
    license_state_region = models.CharField(max_length=100, blank=True)
    agency_name = models.CharField(max_length=100, blank=True)
    agency_office_address = models.TextField(blank=True)
    job_title = models.CharField(max_length=100, blank=True)
    languages_spoken = models.JSONField(default=list, blank=True)
    service_areas = models.JSONField(default=list, blank=True)
    specialties = models.JSONField(default=list, blank=True)
    PREFERRED_ROUTING_CHOICES = [
        ("BOTH", "Both"),
        ("BUYER", "Buyer"),
        ("SELLER", "Seller"),
    ]
    preferred_lead_routing = models.CharField(max_length=20, choices=PREFERRED_ROUTING_CHOICES, blank=True)
    years_of_experience = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f'Agent {self.profile.user.username}'
