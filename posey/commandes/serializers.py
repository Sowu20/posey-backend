from rest_framework import serializers
from commandes.models import Commande, Prestation
from users.serializers import UserSerializer

class RegisterCommandeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Commande
        fields = ['prestation', 'client', 'prestataire', 'statut']
    
class UpdateCommandeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Commande
        fields = ['statut']

class DetailCommandeSerializer(serializers.ModelSerializer):
    prestation = serializers.CharField(source='prestation.titre', read_only=True)
    client = serializers.StringRelatedField()
    prestataire = serializers.CharField(source='prestataire.nom', read_only=True)
    
    class Meta:
        model = Commande
        fields = '__all__'

class CommandeSerializer(serializers.ModelSerializer):
    prestation = serializers.StringRelatedField()
    client = serializers.StringRelatedField()
    prestataire = serializers.StringRelatedField()

    class Meta:
        model = Commande
        fields = ['id', 'client' , 'statut', 'prestation', 'prestataire', 'date_commande']

class PrestationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prestation
        fields = ['id', 'titre', 'description', 'prix', 'client', 'prestataire', 'statut', 'date_demande']