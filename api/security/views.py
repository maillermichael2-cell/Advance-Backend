from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from django.contrib.auth.models import User
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import redirect
from django.conf import settings
import json
import requests

from django.conf import settings
from django.shortcuts import redirect
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.authentication import SessionAuthentication
from .models import Profile, AgentProfile
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken


from .serializers import RegisterSerializer, CustomTokenObtainPairSerializer, CompleteProfileSerializer

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

class CustomTokenObtainPairView(TokenObtainPairView):
    permission_classes = (AllowAny,)
    serializer_class = CustomTokenObtainPairSerializer


def _issue_tokens_and_redirect(user):
    refresh = RefreshToken.for_user(user)
    frontend_redirect_url = f"{settings.FRONTEND_URL.rstrip('/')}/auth/callback"
    return redirect(
        f"{frontend_redirect_url}?access={str(refresh.access_token)}&refresh={str(refresh)}"
    )


class GoogleIssueTokenView(APIView):
    """
    Lands here right after allauth finishes the Google login (session cookie set).
    Branches based on profile completeness instead of issuing tokens blindly.
    """
    authentication_classes = [SessionAuthentication]
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user

        profile = Profile.objects.filter(user=user).first()

        if profile is None:
            # Brand new user — frontend needs to ask: individual or agent?
            return redirect(f"{settings.FRONTEND_URL.rstrip('/')}/auth/complete-profile")

        if profile.role == 'ESTATE AGENT' and not AgentProfile.objects.filter(profile=profile).exists():
            # Chose/has agent role but hasn't filled in agent-specific fields yet
            return redirect(f"{settings.FRONTEND_URL.rstrip('/')}/auth/complete-agent-profile")

        # Fully onboarded — individual, or agent with AgentProfile already filled in
        return _issue_tokens_and_redirect(user)


class CompleteProfileView(APIView):
    """
    Called by the frontend after the user picks a role (and fills agent fields,
    if applicable). Still relies on the session cookie from the Google login —
    no JWT exists yet at this point. Creates Profile/AgentProfile, then issues tokens.
    """
    authentication_classes = [SessionAuthentication]
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = CompleteProfileSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        profile, _ = Profile.objects.update_or_create(
            user=request.user,
            defaults={
                'role': data['role'],
                'phone_number': data.get('phone_number', ''),
            }
        )

        if data['role'] == 'ESTATE AGENT':
            AgentProfile.objects.update_or_create(
                profile=profile,
                defaults={
                    'license_number': data.get('license_number', ''),
                    'license_state_region': data.get('license_state_region', ''),
                    'agency_name': data.get('agency_name', ''),
                    'agency_office_address': data.get('agency_office_address', ''),
                    'job_title': data.get('job_title', ''),
                    'languages_spoken': data.get('languages_spoken', []),
                    'service_areas': data.get('service_areas', []),
                    'specialties': data.get('specialties', []),
                    'preferred_lead_routing': data.get('preferred_lead_routing', ''),
                    'years_of_experience': data.get('years_of_experience'),
                }
            )

        refresh = RefreshToken.for_user(request.user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }, status=status.HTTP_200_OK)