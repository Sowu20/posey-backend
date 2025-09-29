from rest_framework import serializers
from .models import Service

class ServiceSerializer(serializers.ModelSerializer):
    prestataire_nom = serializers.CharField(source="prestataire.nom", read_only=True)
    categorie_nom = serializers.CharField(source="categorie.nom", read_only=True)

    class Meta:
        model = Service
        fields = ['id', 'nom', 'description', 'prix', 'categorie', 'categorie_nom', 'prestataire', 'prestataire_nom', 'date_creation', 'image']
        read_only_fields = ['prestataire', 'date_creation']