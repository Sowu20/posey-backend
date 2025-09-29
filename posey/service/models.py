from django.db import models
from users.models import User
from prestations.models import CategoriePrestation, Prestation

# Create your models here.
class Service(models.Model):
    prestataire = models.ForeignKey(User, on_delete=models.CASCADE, related_name="services")
    categorie = models.ForeignKey(CategoriePrestation, on_delete=models.CASCADE, related_name="categorie_service")
    prestation = models.ForeignKey(Prestation, on_delete=models.CASCADE, related_name="prestation", null=True, blank=True)
    nom = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    prix = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='service_images/', null=True, blank=True)

    def __str__(self):
        return f"{self.nom} - {self.prestataire.nom}"