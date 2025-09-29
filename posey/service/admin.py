from django.contrib import admin
from .models import Service

# Register your models here.
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('prestataire', 'categorie', 'prestation', 'nom', 'description', 'prix', 'date_creation', 'image')

admin.site.register(Service, ServiceAdmin)