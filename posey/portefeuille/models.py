from django.db import models
from users.models import User
from decimal import Decimal
from django.utils import timezone

class Portefeuille(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='portefeuille')
    solde = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    date_mise_a_jour = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Portefeuille de {self.user.username} - Solde: {self.solde}"

class Transaction(models.Model):
    METHODE_PAYEMENT = [
        ('FLOOZ', 'FLOOZ'),
        ('TMONEY', 'TMONEY'),
    ]
    TRANSACTION = [
        ("depot", "Dépôt"),
        ("paiement", "Paiement"),
    ]

    portefeuille = models.ForeignKey(Portefeuille, on_delete=models.CASCADE)
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    type_transaction = models.CharField(max_length=35, choices=TRANSACTION, default='depot')
    methode_payement = models.CharField(max_length=35, choices=METHODE_PAYEMENT, default='TMONEY')
    telephone = models.CharField(max_length=20)
    statut = models.CharField(max_length=20, choices=[
        ('en attente', 'En attente'),
        ('succes', 'Succès'),
        ('echec', 'Échec'),
        ('annule', 'Annulé')
    ], default='en attente')
    identifier = models.CharField(max_length=255, unique=True, blank=True, null=True)
    reference_externe = models.CharField(max_length=255, blank=True, null=True)
    date_transaction = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Transaction {self.montant} {self.statut}"