from rest_framework import serializers
from commandes.models import Commande, Prestation
from users.serializers import UserSerializer
from service.models import Service

class RegisterCommandeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Commande
        fields = ['prestation', 'service', 'client', 'prestataire', 'statut']

    def create(self, validated_data):
        service = validated_data.get('service')
        if service and service.prestation:
            validated_data['prestation'] = service.prestation
        else:
            raise serializers.ValidationError({"service": "Ce service n'est pas lié à une prestation."})
        return super().create(validated_data)
    
class UpdateCommandeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Commande
        fields = ['statut']

class DetailCommandeSerializer(serializers.ModelSerializer):
    prestation = serializers.CharField(source='prestation.titre', read_only=True)
    client = serializers.StringRelatedField()
    prestataire = serializers.CharField(source='prestataire.nom', read_only=True)
    service = serializers.CharField(source='service.nom', read_only=True)
    
    class Meta:
        model = Commande
        fields = '__all__'

class CommandeSerializer(serializers.ModelSerializer):
    titre = serializers.CharField(source='prestation.titre', read_only=True)
    description = serializers.CharField(source='prestation.description', read_only=True)
    prix = serializers.DecimalField(source='prestation.prix', max_digits=10, decimal_places=2, read_only=True)
    client = serializers.StringRelatedField()
    prestataire = serializers.StringRelatedField()

    class Meta:
        model = Commande
        fields = ['id', 'client' , 'statut', 'titre', 'description', 'prix', 'prestataire', 'date_commande']

class PrestationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prestation
        fields = ['id', 'titre', 'description', 'prix', 'client', 'prestataire', 'statut', 'date_demande']