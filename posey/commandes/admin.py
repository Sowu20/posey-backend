from django.contrib import admin
from commandes.models import Commande

class CommandeAdmin(admin.ModelAdmin):
    list_display = ('prestation', 'client', 'prestataire', 'statut', 'date_commande')

admin.site.register(Commande, CommandeAdmin)