import django_filters
from .models import Property


class PropertyFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    category = django_filters.CharFilter(field_name='category__name', lookup_expr='icontains')
    city = django_filters.CharFilter(field_name='city', lookup_expr='icontains')
    bedrooms = django_filters.NumberFilter(field_name='bedrooms', lookup_expr='exact')
    is_available = django_filters.BooleanFilter(field_name='is_available', lookup_expr='exact')

    class Meta:
        model = Property
        fields = ['min_price', 'max_price', 'category', 'city', 'bedrooms', 'is_available']