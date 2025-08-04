from rest_framework import serializers
from prestations.models import CategoriePrestation, Notification, Prestation, DemandeCiblee
from users.models import User
from note.models import Note

# Catégorie
class RegisterCategorieSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriePrestation
        fields = '__all__'
    
class UpdateCategorieSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriePrestation
        fields = ['nom', 'description']

class DetailCategorieSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriePrestation
        fields = '__all__'

# User
class ListePrestataireSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'nom', 'prenom', 'role', 'quartier', 'ville', 'date_inscription']

# Prestation
class RegisterPrestationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prestation
        fields = ['categorie', 'titre', 'description', 'prix', 'client', 'prestataire']
    
class UpdatePrestationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prestation
        fields = ['titre', 'description', 'prix', 'prestataire']

class DetailPrestationSerializer(serializers.ModelSerializer):
    categorie = serializers.StringRelatedField()
    client = serializers.StringRelatedField()
    prestataire = serializers.StringRelatedField()

    class Meta:
        model = Prestation
        fields = '__all__'

class PrestationSerializer(serializers.ModelSerializer):
    client = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)
    client_username = serializers.CharField(source='client.username', read_only=True)
    prestataire = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)
    prestataire_username = serializers.CharField(source='prestataire.username', read_only=True)

    class Meta:
        model = Prestation
        fields = ['id', 'categorie', 'titre', 'description', 'prix', 'client', 'client_username', 'prestataire', 'prestataire_username', 'date_demande', 'statut']


class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ['id', 'score', 'commentaire', 'client']

class CategoriePrestationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriePrestation
        fields = ['id', 'nom']

class PrestationDisponibleSerializer(serializers.ModelSerializer):
    categorie = CategoriePrestationSerializer

    class Meta:
        model = Prestation
        fields = ['id', 'titre', 'description', 'prix', 'categorie', 'date_demande']

class DemandeCibleeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DemandeCiblee
        fields = ['id', 'prestation', 'prestataire', 'date_envoi']

class PrestationRefuseeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prestation
        fields = '__all__'

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'

class PrestationClientSerializer(serializers.ModelSerializer):
    categorie = serializers.CharField(source='categorie.nom', read_only=True)
    prestataire = serializers.CharField(source='prestataire.username', read_only=True)
    date_formatee = serializers.SerializerMethodField()

    class Meta:
        model = Prestation
        fields = ['id', 'titre', 'statut', 'categorie', 'prestataire', 'date_formatee']

    def get_date_formatee(self, obj):
        return obj.date_demande.strftime('%d %b %Y à %H:%M')