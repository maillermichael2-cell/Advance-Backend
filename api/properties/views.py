from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied
from .permissions import IsAgentCreatorOrOwner
from .models import PropertyCategory, Property, Favorite, PropertyImage
from .serializers import (
    PropertyCategorySerializer,
    PropertySerializer,
    FavoriteSerializer,
    PropertyImageSerializer,
)


class PropertyCategoryListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = PropertyCategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return PropertyCategory.objects.all()


class PropertyCategoryRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PropertyCategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return PropertyCategory.objects.all()


class PropertyListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = PropertySerializer
    permission_classes = [IsAgentCreatorOrOwner]

    def get_queryset(self):
        qs = Property.objects.all().select_related('category', 'owner').prefetch_related('images')
        user = self.request.user
        try:
            is_agent = user.is_authenticated and user.profile.role == 'ESTATE AGENT'
        except Exception:
            is_agent = False

        if is_agent:
            return qs.filter(owner=user)
        return qs

    def perform_create(self, serializer):
        # Ensure the authenticated user is an agent (permission also checks this)
        user = self.request.user
        try:
            is_agent = user.is_authenticated and user.profile.role == 'ESTATE AGENT'
        except Exception:
            is_agent = False

        if not is_agent:
            raise PermissionDenied('Only estate agents may create properties.')

        serializer.save(owner=user)


class PropertyRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PropertySerializer
    permission_classes = [IsAgentCreatorOrOwner]

    def get_queryset(self):
        return Property.objects.all().select_related('category', 'owner').prefetch_related('images')


class FavoriteListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user).select_related('property')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class FavoriteRetrieveDestroyAPIView(generics.RetrieveDestroyAPIView):
    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Favorite.objects.all().select_related('property')


class PropertyImageListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = PropertyImageSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = PropertyImage.objects.all().select_related('property')
        property_id = self.request.query_params.get('property_id')
        if property_id is not None:
            queryset = queryset.filter(property_id=property_id)
        return queryset


class PropertyImageRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PropertyImageSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return PropertyImage.objects.all().select_related('property')
