from django.db import models
from users.models import User
from prestations.models import Prestation
from service.models import Service

class Commande(models.Model):
    STATUT_CHOICE = [
        ('en attente', 'En attente'),
        ('accepte', 'Acceptée'),
        ('termine', 'Terminé'),
    ]
    prestation = models.ForeignKey(Prestation, on_delete=models.CASCADE)
    client = models.ForeignKey(User, related_name='client', on_delete=models.CASCADE)
    prestataire = models.ForeignKey(User, related_name='prestataire', on_delete=models.CASCADE, null=True)
    service = models.ForeignKey(Service, related_name='service', on_delete=models.CASCADE, null=True)
    date_commande = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICE, default='en attente')