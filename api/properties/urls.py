from django.urls import path
from .views import (
    PropertyCategoryListCreateAPIView,
    PropertyCategoryRetrieveUpdateDestroyAPIView,
    PropertyListCreateAPIView,
    PropertyRetrieveUpdateDestroyAPIView,
    FavoriteListCreateAPIView,
    FavoriteRetrieveDestroyAPIView,
    PropertyImageListCreateAPIView,
    PropertyImageRetrieveUpdateDestroyAPIView,
)

urlpatterns = [
    path('properties/categories/', PropertyCategoryListCreateAPIView.as_view(), name='propertycategory-list'),
    path('properties/categories/<int:pk>/', PropertyCategoryRetrieveUpdateDestroyAPIView.as_view(), name='propertycategory-detail'),
    path('properties/', PropertyListCreateAPIView.as_view(), name='property-list'),
    path('properties/<int:pk>/', PropertyRetrieveUpdateDestroyAPIView.as_view(), name='property-detail'),
    path('favorites/', FavoriteListCreateAPIView.as_view(), name='favorite-list'),
    path('favorites/<int:pk>/', FavoriteRetrieveDestroyAPIView.as_view(), name='favorite-detail'),
    path('property-images/', PropertyImageListCreateAPIView.as_view(), name='propertyimage-list'),
    path('property-images/<int:pk>/', PropertyImageRetrieveUpdateDestroyAPIView.as_view(), name='propertyimage-detail'),
]
