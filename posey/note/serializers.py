from rest_framework import serializers
from note.models import Note 
from users.models import User
from commandes.models import Commande
from users.serializers import UserSerializer
from commandes.serializers import CommandeSerializer

class RegisterNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ['client', 'prestataire', 'commande', 'commentaire', 'score']

    def validate(self, data):
        # Empêche de noter deux fois la même commande par un même client
        if Note.objects.filter(client=data['client'], commande=data['commande']).exists():
            raise serializers.ValidationError("Vous avez déjà noté cette commande.")
        return data

class DetailNoteSerializer(serializers.ModelSerializer):
    client = serializers.StringRelatedField()

    class Meta:
        model = Note
        fields = '__all__'

class NoteSerializer(serializers.ModelSerializer):
    client = UserSerializer(read_only=True)
    commande = CommandeSerializer(read_only=True)

    class Meta:
        model = Note
        fields = '__all__'

class TopPrestataireSerializer(serializers.ModelSerializer):
    moyenne_notes = serializers.FloatField()
    nombre_notes = serializers.IntegerField()

    class Meta:
        model = User
        fields = ['id', 'nom', 'prenom', 'image', 'moyenne_notes', 'nombre_notes']

class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ['id', 'client', 'prestataire', 'commande', 'commentaire', 'score']

    def validate_score(self, value):
        if value > 5:
            raise serializers.ValidationError("Le score ne peut pas dépasser 5.")
        return value
    
class CommentaireNoteSerializer(serializers.ModelSerializer):
    client = serializers.SerializerMethodField()

    class Meta:
        model = Note
        fields = ['id', 'client', 'commentaire', 'score']

    def get_client_nom(self, obj):
        return f"{obj.client.nom} {obj.client.prenom}"