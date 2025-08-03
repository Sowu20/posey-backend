from django.db import models
from users.models import User
from commandes.models import Commande

class Note(models.Model):
    client = models.ForeignKey(User, on_delete=models.CASCADE)
    prestataire = models.ForeignKey(User, on_delete=models.CASCADE, related_name='prestataire_notes')
    commande = models.ForeignKey(Commande, on_delete=models.CASCADE, null=True, blank=True) 
    commentaire = models.TextField(blank=True, null=True)
    score = models.PositiveIntegerField()
    # class Meta:
    #     unique_together = ('client', 'commande')