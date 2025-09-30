from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from .permissions import IsAdmin, IsClient, IsPrestataire
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import RetrieveAPIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from users.models import User
from users.serializers import PrestataireSerializer, PrestataireDetailSerializer,  UserDetailSerializer, UserSerializer, LoginSerializer, RegisterSerializer, UpdateSerializer, DetailSerializer, UserListByLocationSerializer, UserListByRoleSerializer, PrestataireSerializer, UserListByQuartierSerializer, UserListByVilleSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer 

    @swagger_auto_schema(
        operation_description="Créer un nouveau compte utilisateur.",
        responses={201: "Utilisateur créé avec succès", 400: "Données invalides"}
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
    
class UpdateView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UpdateSerializer 
    lookup_field = 'id'

    @swagger_auto_schema(
        operation_description="Modifier un nouveau compte utilisateur.",
        responses={201: "Utilisateur modifié avec succès", 400: "Données non modifié"}
    )
    def put(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
class GetView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = DetailSerializer

    @swagger_auto_schema(
        responses={201: "Liste des utilisateurs", 400: "Données invalides"}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
class DeleteView(APIView):
    def delete(self, request, id, *args, **kwargs):
        try:
            user = User.objects.get(id=id)
            user.delete()
            return Response({"Utilisateur supprimé avec succès."}, status=204)
        except User.DoesNotExist:
            return Response({"Utilisateur introuvable."}, status=400)
        
class UsersByLocationView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserListByLocationSerializer

    def get_queryset(self):
        quartier = self.request.query_params.get('quartier')
        ville = self.request.query_params.get('ville')
        queryset = User.objects.filter(role__in=['client', 'prestataire'])

        if quartier:
            queryset = queryset.filter(quartier__iexact=quartier)
        if ville:
            queryset = queryset.filter(ville__iexact=ville)

        return queryset
    
class UsersByQuartierView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserListByQuartierSerializer

    def get_queryset(self):
        quartier = self.request.query_params.get('quartier')
        queryset = User.objects.filter(role__in=['client', 'prestataire'])

        if quartier:
            queryset = queryset.filter(quartier__iexact=quartier)

        return queryset
    
class UsersByVilleView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserListByVilleSerializer

    def get_queryset(self):
        ville = self.request.query_params.get('ville')
        queryset = User.objects.filter(role__in=['client', 'prestataire'])

        if ville:
            queryset = queryset.filter(ville__iexact=ville)

        return queryset

class UsersByRoleView(generics.ListAPIView):
    serializer_class = UserListByRoleSerializer

    def get_queryset(self):
        role = self.request.query_params.get('role')
        valid_roles = ['client', 'prestataire', 'admin']
        if role in valid_roles:
            return User.objects.filter(role__iexact=role)
        return User.objects.filter(role__in=valid_roles)
    
class PrestatairesAvecCategorieView(APIView):
    def get(self, request):
        prestataires = User.objects.filter(role='prestataire', categorie__isnull=False)
        serializer = PrestataireSerializer(prestataires, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class ListePrestataireParCategorieView(APIView):
    def get(self, request):
        categorie_id = request.query_params.get('categorie')
        if not categorie_id:
            return Response([])

        prestataires = User.objects.filter(
            role='prestataire',
            categorie_id=categorie_id
        )

        serializer = UserSerializer(prestataires, many=True)
        return Response(serializer.data)
    
class LoginAPIView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            user_data = UserSerializer(user).data

            return Response({
                'user': user_data,
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class PrestataireListView(generics.ListAPIView):
    serializer_class = PrestataireSerializer

    def get_queryset(self):
        return User.objects.filter(role='prestataire')
    
class UserDetailByIdView(RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserDetailSerializer
    lookup_field = 'id'

class PrestataireDetailView(APIView):
    def get(self, request, id):
        user = get_object_or_404(User, id=id, role='prestataire')
        serializer = PrestataireDetailSerializer(user)

        return Response(serializer.data)
    
class AdminOnlyView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        return Response({"message": "Bienvenue Admin !"}, status=status.HTTP_200_OK)
    
class ResetPasswordView(APIView):
    def post(self, request):
        email = request.data.get("email")
        try:
            user = User.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)

            reset_link = f"https://posey-frontend-y8so.vercel.app/reset-password/{uid}/{token}/"

            send_mail(
                "Réinitialisation de mot de passe",
                f"Cliquez sur ce lien pour réinitialiser votre mot de passe : {reset_link}",
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            return Response({"message": "Lien de réinitialisation envoyé."}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "Aucun utilisateur trouvé avec cet email."}, status=status.HTTP_404_NOT_FOUND)
            
class ResetPasswordConfirmView(APIView):
    def post(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({"error": "Lien invalide"}, status=status.HTTP_400_BAD_REQUEST)

        if not default_token_generator.check_token(user, token):
            return Response({"error": "Token invalide ou expiré"}, status=status.HTTP_400_BAD_REQUEST)

        new_password = request.data.get("password")
        if not new_password:
            return Response({"error": "Le mot de passe est requis"}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        return Response({"message": "Mot de passe réinitialisé avec succès"}, status=status.HTTP_200_OK)
    
class ChangePasswordView(APIView):
    # permission_classes = [permissions.IsAuthenticated]

    def put(self, request):
        user = request.user
        new_password = request.data.get("new_password")

        if not new_password:
            return Response({"error": "Le nouveau mot de passe est requis"}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        return Response({"message": "Mot de passe changé avec succès"}, status=status.HTTP_200_OK)