from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from .permissions import IsAdmin, IsClient, IsPrestataire
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import RetrieveAPIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse
from users.models import User, Messages, ResetPasswordToken
from prestations.models import CategoriePrestation
from users.serializers import PrestataireSerializer, PrestataireDetailSerializer,  UserDetailSerializer, UserSerializer, LoginSerializer, RegisterSerializer, UpdateSerializer, DetailSerializer, UserListByLocationSerializer, UserListByRoleSerializer, PrestataireSerializer, ListePrestataireSerializer, UserListByQuartierSerializer, UserListByVilleSerializer, ResetPasswordSerializer, ResetPasswordConfirmSerializer
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
        serializer = ResetPasswordSerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = User.objects.get(email=email)
                ResetPasswordToken.objects.filter(user=user, is_used=False).update(is_used=True)
                reset_token = ResetPasswordToken.objects.create(user=user)

                reset_url = f"https://posey-frontend-y8so.vercel.app/reset_password/{reset_token.token}"

                send_mail(
                    "Réinitialisation de votre de passe"
                    f"""
                        Bonjour {user.prenom},
                        Vous avez demandé la réinitialisation de votre mot de passe:
                        {reset_url}
                        Ce lien expirera dans 1 heure
                     """,
                    settings.DEFAULT_FROM_EMAIL
                    [email],
                    fail_silently=False
                )

                return Response({
                    'message': 'Un email de réinitialisation a été envoyé à votre adresse.'
                }, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({
                    'message': 'Un email de réinitialisation a été envoyé à votre adresse.'
                }, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({
                    'error': 'Erreur lors de l\'envoi de l\'email. Veuillez réessayer plus tard.'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
class ResetPasswordConfirmView(APIView):
    def post(self, request):
        serializer = ResetPasswordConfirmSerializer(data=request.data)

        if serializer.is_valid():
            token = serializer.validated_data['token']
            new_password = serializer.validated_data['new_password']
            try:
                reset_token = ResetPasswordToken.objects.get(token=token, is_used=False)
                if reset_token.is_expired():
                    return Response({
                        'error': 'Le token a expiré. Veuillez faire une nouvelle demande.'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                user = reset_token.user
                user.set_password(new_password)
                user.save()

                reset_token.is_used = True
                reset_token.save()

                return Response({
                    'message': 'Votre mot de passe a été réinitialisé avec succès.'
                }, status=status.HTTP_200_OK)
            except ResetPasswordToken.DoesNotExist:
                return Response({
                    'error': 'Token invalide ou déjà utilisé.'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ResetPasswordTokenValidateView(APIView):
    def get(request, token):
        try:
            reset_token = ResetPasswordToken.objects.get(token=token, is_used=False)
            
            if reset_token.is_expired():
                return Response({
                    'valid': False,
                    'error': 'Le token a expiré.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            return Response({
                'valid': True,
                'user_email': reset_token.user.email
            }, status=status.HTTP_200_OK)
            
        except ResetPasswordToken.DoesNotExist:
            return Response({
                'valid': False,
                'error': 'Token invalide.'
            }, status=status.HTTP_400_BAD_REQUEST)