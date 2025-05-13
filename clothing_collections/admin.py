from django.contrib import admin

from clothing_collections.models import Collection, CollectionAccessRequest

# Register your models here.
admin.site.register(Collection)
admin.site.register(CollectionAccessRequest)