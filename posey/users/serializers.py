from rest_framework import serializers
from django.contrib.auth import authenticate
from django.core.validators import validate_email
from django.contrib.auth.password_validation import validate_password
from users.models import User
from prestations.models import CategoriePrestation

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    categorie = serializers.PrimaryKeyRelatedField(
        queryset=CategoriePrestation.objects.all(), required=False
    )

    class Meta:
        model = User
        fields = ('username', 'nom', 'prenom', 'email', 'password' , 'role', 'quartier', 'ville', 'categorie')

    def validate(self, data):
        if data.get('role') == 'prestataire' and not data.get('categorie'):
            raise serializers.ValidationError({
                'categorie': "Veuillez ajouter le champ categorie si vous êtes un prestataire."
            })
        return data

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            nom=validated_data['nom'],
            prenom=validated_data['prenom'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            role=validated_data['role'],
            quartier=validated_data['quartier'],
            ville=validated_data['ville'],
            categorie=validated_data.get('categorie', None)
        )
        return user
    
class UpdateSerializer(serializers.ModelSerializer):
    categorie = serializers.CharField(source='categorie.nom', read_only=True)

    class Meta:
        model = User
        fields = ('username', 'nom', 'prenom', 'email', 'role', 'quartier', 'ville', 'categorie')
        extra_kwargs = {
            'email': {'required': False},
            'username': {'required': False},
            'role': {'required': False},
        }

class DetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'nom', 'prenom', 'email', 'role', 'quartier', 'ville', 'date_inscription', 'image')
        
    def to_representation(self, instance):
        data = super().to_representation(instance)

        if instance.role == 'prestataire' and instance.categorie:
            data['categorie'] = {
                'nom': instance.categorie.nom,
            }

        return data

class UserListByLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'nom', 'prenom', 'email', 'role', 'ville', 'quartier', 'date_inscription']

class UserListByQuartierSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'nom', 'prenom', 'email', 'role', 'quartier', 'date_inscription']

class UserListByVilleSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'nom', 'prenom', 'email', 'role', 'ville', 'date_inscription']

class UserListByRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'nom', 'prenom', 'email', 'role', 'ville', 'quartier', 'date_inscription']

class CategoriePrestationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriePrestation
        fields = ['id', 'nom', 'description']

class PrestataireSerializer(serializers.ModelSerializer):
    categorie = CategoriePrestationSerializer()
    class Meta:
        model = User
        fields = ['id', 'username', 'nom', 'prenom', 'email', 'ville', 'quartier', 'categorie']

class ListePrestataireSerializer(serializers.ModelSerializer):
    categorie = CategoriePrestationSerializer()
    class Meta:
        model = User
        fields = ['id', 'nom', 'prenom', 'email', 'role', 'ville', 'quartier', 'categorie']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'nom', 'prenom', 'email', 'role', 'quartier', 'ville', 'image']

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                if not user.is_active:
                    raise serializers.ValidationError("Ce compte est inactif.")
                data['user'] = user
            else:
                raise serializers.ValidationError("Nom d'utilisateur ou mot de passe incorrect.")
        else:
            raise serializers.ValidationError("Les trois champs sont obligatoires.")
        
        return data
    
class PrestataireSerializer(serializers.ModelSerializer):
    categorie = serializers.CharField(source='categorie.nom', read_only=True)
    class Meta:
        model = User
        fields = ['id', 'username', 'nom', 'prenom', 'image', 'quartier', 'ville', 'categorie']

class CategoriePrestationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriePrestation
        fields = ['id', 'nom'] 

class UserDetailSerializer(serializers.ModelSerializer):
    categorie = CategoriePrestationSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'nom', 'prenom', 'image', 'role', 'quartier', 'ville', 'date_inscription', 'categorie']

class PrestataireDetailSerializer(serializers.ModelSerializer):
    categorie = serializers.CharField(source='categorie.nom', read_only=True)
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'nom', 'prenom', 'image', 'categorie', 'quartier', 'ville']