from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Profile, AgentProfile

# 1. LOGIN SERIALIZER (Injects the role into the JWT token payload)
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Safely fetch the role from your Profile model
        try:
            role = user.profile.role
        except Exception:
            role = "INDIVIDUAL"  # Fallback option

        # Inject custom claims into the JWT token
        token['role'] = role
        token['username'] = user.username
        
        return token


# 2. SUB-SERIALIZERS
class UserCreateSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True, validators=[UniqueValidator(queryset=User.objects.all(), message="A user with this username already exists.")])
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all(), message="A user with this email already exists.")]
    )
    password = serializers.CharField(write_only=True, required=True, min_length=8)

    class Meta:
        model = User
        fields = ('username', 'email', 'password')


class AgentMetaSerializer(serializers.Serializer):
    license_number = serializers.CharField(required=False)
    license_state_region = serializers.CharField(required=False, allow_blank=True)
    agency_name = serializers.CharField(required=False, allow_blank=True)
    agency_office_address = serializers.CharField(required=False, allow_blank=True)
    job_title = serializers.CharField(required=False, allow_blank=True)
    languages_spoken = serializers.CharField( required=False, default='Null')
    service_areas = serializers.CharField( required=False, default='Null')
    specialties = serializers.CharField( required=False, default='Null')
    preferred_lead_routing = serializers.ChoiceField(choices=AgentProfile.PREFERRED_ROUTING_CHOICES, required=False, allow_blank=True)
    years_of_experience = serializers.IntegerField(required=False, allow_null=True)


class CompleteProfileSerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=Profile.ROLE_CHOICES)
    phone_number = serializers.CharField(required=False, allow_blank=True)

    # Agent-only fields — required only if role == 'ESTATE AGENT'
    license_number = serializers.CharField(required=False, allow_blank=True)
    license_state_region = serializers.CharField(required=False, allow_blank=True)
    agency_name = serializers.CharField(required=False, allow_blank=True)
    agency_office_address = serializers.CharField(required=False, allow_blank=True)
    job_title = serializers.CharField(required=False, allow_blank=True)
    languages_spoken = serializers.CharField(required=False, default='Null')
    service_areas = serializers.CharField(required=False, default='Null')
    specialties = serializers.CharField(required=False, default='Null')
    preferred_lead_routing = serializers.ChoiceField(
        choices=AgentProfile.PREFERRED_ROUTING_CHOICES, required=False, allow_blank=True
    )
    years_of_experience = serializers.IntegerField(required=False, allow_null=True)

    def validate(self, data):
        if data['role'] == 'ESTATE AGENT' and not data.get('license_number'):
            raise serializers.ValidationError(
                {'license_number': 'License number is required for estate agents.'}
            )
        return data




# 3. ROOT REGISTRATION SERIALIZER
class RegisterSerializer(serializers.Serializer):
    # Accept either a nested `user` object or top-level user fields
    user = UserCreateSerializer(required=False)
    # # Top-level user fields (optional alternative to nested `user`)
    # username = serializers.CharField(required=False)
    # email = serializers.EmailField(required=False)
    # password = serializers.CharField(write_only=True, required=False, min_length=8)
    role = serializers.ChoiceField(choices=Profile.ROLE_CHOICES, required=True)
    phone_number = serializers.CharField(required=False, allow_blank=True)
    

    def validate(self, attrs):
        role = attrs.get('role')
        agent_meta = attrs.get('agent_meta')

        # If `user` not provided, ensure top-level user fields exist
        if not attrs.get('user'):
            if not attrs.get('email') or not attrs.get('password') or not attrs.get('username'):
                raise serializers.ValidationError({"user": "Provide nested `user` or top-level `username`, `email` and `password`."})
            # build nested user dict for downstream logic
            attrs['user'] = {
                'username': attrs.pop('username'),
                'email': attrs.pop('email'),
                'password': attrs.pop('password')
            }

        if role == 'ESTATE AGENT' and not agent_meta:
            raise serializers.ValidationError({"agent_meta": "Agent meta is required for Estate Agents."})

        return attrs

    def create(self, validated_data):
        user_data = validated_data.get('user')
        role = validated_data.get('role')
        phone_number = validated_data.get('phone_number', '')
        agent_meta = validated_data.get('agent_meta') or {}

        email = user_data.get('email')
        username = email  # Map email directly to username

        user = User.objects.create_user(
            username=user_data.get('username') or username,
            email=email,
            password=user_data.get('password')
        )

        profile = Profile.objects.create(
            user=user,
            role=role,
            phone_number=phone_number
        )

        if role == 'ESTATE AGENT' and agent_meta:
            AgentProfile.objects.create(
                profile=profile,
                license_number=agent_meta.get('license_number', ''),
                license_state_region=agent_meta.get('license_state_region', ''),
                agency_name=agent_meta.get('agency_name', ''),
                agency_office_address=agent_meta.get('agency_office_address', ''),
                job_title=agent_meta.get('job_title', ''),
                languages_spoken=agent_meta.get('languages_spoken', []),
                service_areas=agent_meta.get('service_areas', []),
                specialties=agent_meta.get('specialties', []),
                preferred_lead_routing=agent_meta.get('preferred_lead_routing', ''),
                years_of_experience=agent_meta.get('years_of_experience', None)
            )

        return user

    # Converts the raw User instance output back into a customized confirmation payload
    def to_representation(self, instance):
        return {
            "message": "User registered successfully.",
            "user": {
                "username": instance.username,
                "email": instance.email
            },
            "role": instance.profile.role,
            "phone_number": instance.profile.phone_number,
            "agent_meta": {
                **({
                    "license_number": instance.profile.agent_meta.license_number,
                    "license_state_region": instance.profile.agent_meta.license_state_region,
                    "agency_name": instance.profile.agent_meta.agency_name,
                    "agency_office_address": instance.profile.agent_meta.agency_office_address,
                    "job_title": instance.profile.agent_meta.job_title,
                    "languages_spoken": instance.profile.agent_meta.languages_spoken,
                    "service_areas": instance.profile.agent_meta.service_areas,
                    "specialties": instance.profile.agent_meta.specialties,
                    "preferred_lead_routing": instance.profile.agent_meta.preferred_lead_routing,
                    "years_of_experience": instance.profile.agent_meta.years_of_experience,
                } if hasattr(instance, 'profile') and hasattr(instance.profile, 'agent_meta') else {})
            }
        }
