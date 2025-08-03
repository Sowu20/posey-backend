from django.db import models
from users.models import User
from prestations.models import Prestation

class Commande(models.Model):
    STATUT_CHOICE = [
        ('en attente', 'En attente'),
        ('accepte', 'Acceptée'),
        ('termine', 'Terminé'),
    ]
    prestation = models.ForeignKey(Prestation, on_delete=models.CASCADE)
    client = models.ForeignKey(User, related_name='client', on_delete=models.CASCADE)
    prestataire = models.ForeignKey(User, related_name='prestataire', on_delete=models.CASCADE)
    date_commande = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICE, default='en attente')