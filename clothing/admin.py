from django.contrib import admin
from .models import Tag, ClothingItem

# Register your models here.
class TagAdmin(admin.ModelAdmin):
    list_display = ('category', 'size', 'color')

class ClothingItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'availability', 'availability_date', 'available', 'owner')
    filter_horizontal = ('tags',)  # Allows selecting multiple tags in a user-friendly way

admin.site.register(Tag, TagAdmin)
admin.site.register(ClothingItem, ClothingItemAdmin)
