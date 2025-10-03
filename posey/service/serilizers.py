from rest_framework import serializers
from .models import Service

class ServiceSerializer(serializers.ModelSerializer):
    prestataire_nom = serializers.CharField(source="prestataire.nom", read_only=True)
    categorie_nom = serializers.CharField(source="categorie.nom", read_only=True)
    prestation_categorie = serializers.CharField(source="prestation.categorie", read_only=True)

    class Meta:
        model = Service
        fields = ['id', 'nom', 'description', 'prix', 'categorie', 'categorie_nom', 'prestataire', 'prestataire_nom', 'prestation', 'prestation_categorie', 'date_creation', 'image']
        read_only_fields = ['date_creation']