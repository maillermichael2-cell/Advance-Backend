import logging

from django.conf import settings
from django.shortcuts import redirect
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth.models import User
from rest_framework import generics

from .models import AgentProfile, Profile
from .serializers import (
    CompleteProfileSerializer,
    CustomTokenObtainPairSerializer,
    RegisterSerializer,
)

logger = logging.getLogger(__name__)


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer


class CustomTokenObtainPairView(TokenObtainPairView):
    permission_classes = (AllowAny,)
    serializer_class = CustomTokenObtainPairSerializer


def _build_frontend_url(path: str) -> str:
    """
    Builds an absolute URL on the frontend domain. `path` must be a
    frontend route (e.g. '/auth/callback'), never a backend API path.
    """
    return f"{settings.FRONTEND_URL.rstrip('/')}{path}"


def _issue_tokens_and_redirect(user):
    refresh = RefreshToken.for_user(user)
    # NOTE: tokens are passed via query string here for simplicity. This is
    # visible in browser history, referrer headers, and server access logs.
    # For a production-hardened flow, prefer one of:
    #   - a short-lived, single-use opaque code exchanged via a follow-up
    #     POST request (the code is looked up server-side for the real JWTs)
    #   - setting the tokens as httpOnly, Secure, SameSite cookies directly
    #     on this redirect response instead of putting them in the URL
    target = _build_frontend_url(
        f"/auth/callback?access={refresh.access_token}&refresh={refresh}"
    )
    return redirect(target)


class GoogleIssueTokenView(APIView):
    """
    Reached via LOGIN_REDIRECT_URL immediately after allauth completes the
    Google OAuth flow and establishes a Django session for request.user.

    Branches based on onboarding completeness:
      - no Profile yet              -> frontend role-selection page
      - agent role, no AgentProfile -> frontend agent-details page
      - otherwise                   -> issue JWTs, send to frontend callback
    """
    authentication_classes = [SessionAuthentication]
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user
        profile = Profile.objects.filter(user=user).first()

        if profile is None:
            return redirect(_build_frontend_url('/auth/complete-profile'))

        if profile.role == 'ESTATE AGENT' and not AgentProfile.objects.filter(profile=profile).exists():
            return redirect(_build_frontend_url('/auth/complete-agent-profile'))

        return _issue_tokens_and_redirect(user)


class CompleteProfileView(APIView):
    """
    Called by the frontend after the user selects a role (and, for agents,
    fills in agent-specific fields). Authenticated via the session cookie
    set during the Google login — no JWT exists yet at this point.
    Creates/updates Profile (and AgentProfile, if applicable) and returns
    JWT tokens directly in the JSON response body.
    """
    authentication_classes = [SessionAuthentication]
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = CompleteProfileSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
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
        except Exception:
            logger.exception("Failed to complete profile for user_id=%s", request.user.id)
            return Response(
                {'error': 'Could not complete profile. Please try again.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        refresh = RefreshToken.for_user(request.user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }, status=status.HTTP_200_OK)