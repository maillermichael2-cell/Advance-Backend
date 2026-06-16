from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from .models import PropertyCategory, Property, Favorite, PropertyImage


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class PropertyCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyCategory
        fields = ['id', 'name', 'slug']


class PropertyImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyImage
        fields = ['id', 'property', 'image', 'uploaded_at', 'order']
        read_only_fields = ['uploaded_at']


class FavoriteSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Favorite
        fields = ['id', 'user', 'property', 'created_at']
        read_only_fields = ['created_at']
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=['user', 'property'],
                message='This property is already in the user favorites list.'
            )
        ]


class PropertySerializer(serializers.ModelSerializer):
    category_detail = PropertyCategorySerializer(source='category', read_only=True)
    owner_detail = UserSerializer(source='owner', read_only=True)
    images = PropertyImageSerializer(many=True, read_only=True)
    category = serializers.PrimaryKeyRelatedField(queryset=PropertyCategory.objects.all())
    owner = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False,
        allow_null=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Property
        fields = [
            'id',
            'title',
            'property_address',
            'description',
            'price',
            'category',
            'category_detail',
            'owner',
            'owner_detail',
            'status',
            'created_at',
            'registered_survey',
            'deed_of_assignment',
            'building_plan_approval',
            'c_of_o',
            'governors_consent',
            'land_size',
            'sq_meters',
            'unit_size',
            'construction_status',
            'number_of_bedrooms',
            'number_of_bathrooms',
            'images',
        ]
        read_only_fields = ['created_at', 'owner_detail', 'category_detail', 'images']
