from django.contrib import admin
from prestations.models import CategoriePrestation, Prestation

# Register your models here.
class CategoriePrestationAdmin(admin.ModelAdmin):
    list_display = ('nom', 'description')

class PrestationAdmin(admin.ModelAdmin):
    list_display = ('categorie', 'titre', 'description', 'prix', 'client', 'date_demande', 'prestataire')

admin.site.register(CategoriePrestation, CategoriePrestationAdmin)
admin.site.register(Prestation, PrestationAdmin)