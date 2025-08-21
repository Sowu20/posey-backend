from django.db import models
from django.conf import settings

class CategoriePrestation(models.Model):
    nom = models.CharField(max_length=50)
    description = models.TextField()

class Prestation(models.Model):
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('accepte', 'Acceptée'),
        ('terminee', 'Terminée'),
        ('annulee', 'Annulée'),
        ('refusee', 'Refusée')
    ]
    categorie = models.ForeignKey(CategoriePrestation, on_delete=models.CASCADE)
    titre = models.CharField(max_length=50)
    description = models.TextField()
    prix = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    client = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='client_prestataire', on_delete=models.CASCADE, null=False)
    date_demande = models.DateTimeField(auto_now_add=True)
    prestataire = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='prestaion_prestataire', on_delete=models.CASCADE, null=True, blank=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    def accepte(self, user):
        if self.statut == 'en_attente':
            if self.prestataire is None:
                self.prestataire = user
            elif self.prestataire != user:
                return False
            self.statut = 'accepte'
            self.save()
            return True
        return False

    def refuse(self, user):
        if self.statut == 'en_attente' and (self.prestataire is None or self.prestataire == user):
            self.statut = 'refusee'
            self.save()
            return True
        return False

class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    prestation = models.ForeignKey(Prestation, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Notification pour {self.user.username}"
    
class DemandeCiblee(models.Model):
    prestation = models.ForeignKey(Prestation, on_delete=models.CASCADE, related_name='demandes_ciblees')
    prestataire = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='demandes_recues')
    date_envoi = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('prestation', 'prestataire')

    def __str__(self):
        return f"Demande pour {self.prestataire} concernant '{self.prestation.titre}'"