import uuid
from django.db import models
from django.utils import timezone
from prestations.models import CategoriePrestation
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLES_CHOICES = [
        ('admin', 'Administrateur'),
        ('client', 'Client'),
        ('prestataire', 'Prestataire'),
    ]
    nom = models.CharField(max_length=50)
    prenom = models.CharField(max_length=65)
    image = models.ImageField(upload_to="users/", blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLES_CHOICES)
    quartier = models.CharField(max_length=50)
    ville = models.CharField(max_length=50)
    date_inscription = models.DateField(auto_now_add=True)
    categorie = models.ForeignKey(CategoriePrestation, on_delete=models.CASCADE, null=True, blank=True, related_name='prestataire')
    est_prestataire = models.BooleanField(default=False)
    est_valide = models.BooleanField(default=False)

class Messages(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    contenu = models.TextField()
    date_envoie = models.DateTimeField(auto_now_add=True)