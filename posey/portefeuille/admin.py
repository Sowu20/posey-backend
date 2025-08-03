from django.contrib import admin
from portefeuille.models import Portefeuille, Transaction

# Register your models here.
class PortefeuilleAdmin(admin.ModelAdmin):
    list_display = ('user', 'solde', 'date_mise_a_jour')

class TransactionAdmin(admin.ModelAdmin):
    list_display = ('portefeuille', 'montant', 'type_transaction', 'methode_payement', 'telephone', 'statut', 'date_transaction', 'reference_externe')

admin.site.register(Portefeuille, PortefeuilleAdmin)
admin.site.register(Transaction, TransactionAdmin)