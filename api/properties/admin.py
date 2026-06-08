from django.contrib import admin
from .models import PropertyCategory, Property, Favorite, PropertyImage

class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 10
    fields = ('image', 'order', 'uploaded_at')
    readonly_fields = ('uploaded_at',)

@admin.register(PropertyCategory)
class PropertyCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name', 'slug')

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'category', 'owner', 'price', 'created_at')
    list_filter = ('status', 'category', 'created_at')
    search_fields = ('title', 'property_address', 'description', 'owner__username')
    raw_id_fields = ('owner',)
    autocomplete_fields = ('category',)
    inlines = [PropertyImageInline]

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'property', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'property__title')
    raw_id_fields = ('user', 'property')

@admin.register(PropertyImage)
class PropertyImageAdmin(admin.ModelAdmin):
    list_display = ('property', 'order', 'uploaded_at')
    list_filter = ('uploaded_at',)
    search_fields = ('property__title',)
    raw_id_fields = ('property',)

