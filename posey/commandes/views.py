from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from users.permissions import IsAdmin, IsClient, IsPrestataire
from users.models import User
from commandes.models import Commande
from commandes.serializers import RegisterCommandeSerializer, UpdateCommandeSerializer, DetailCommandeSerializer, CommandeSerializer

class RegisterCommandeView(generics.CreateAPIView):
    queryset = Commande.objects.all()
    serializer_class = RegisterCommandeSerializer
    
    @swagger_auto_schema(
        operation_description="Créer une nouvelle commande.",
        responses={201: "Commande créé avec succès", 400: "Données invalides"}
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
    
class UpdateCommandeView(generics.UpdateAPIView):
    queryset = Commande.objects.all()
    serializer_class = UpdateCommandeSerializer
    lookup_field = 'id'

    @swagger_auto_schema(
        operation_description="Modifier une commande.",
        responses={201: "Commande modifié avec succès", 400: "Données non modifié"}
    )
    def put(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
class GetCommandeView(generics.ListAPIView):
    queryset = Commande.objects.all()
    serializer_class = DetailCommandeSerializer

    @swagger_auto_schema(
        responses={201: "Liste des commandes", 400: "Données invalides"}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
class DeleteCommandeView(APIView):
    def delete(self, request, id, *args, **kwargs):
        try:
            commande = Commande.objects.get(id=id)
            commande.delete()
            return Response({"Commande supprimée avec succès."}, status=204)
        except Commande.DoesNotExist:
            return Response({"Commande introuvable."}, status=400)
        
# Liste des commandes par client ID
class CommandesParClientView(generics.ListAPIView):
    serializer_class = CommandeSerializer

    def get_queryset(self):
        client_id = self.kwargs['id']
        return Commande.objects.filter(id=client_id)


# Liste des commandes par statut
class CommandesParStatutView(APIView):
    def get(self, request):
        statut = request.query_params.get('statut')
        if statut:
            commandes = Commande.objects.filter(statut=statut)
        else:
            commandes = Commande.objects.all()
        serializer = CommandeSerializer(commandes, many=True)
        return Response(serializer.data)


# Modifier le statut d'une commande
class ChangerStatutCommandeView(APIView):
    def put(self, request, id):
        commande = get_object_or_404(Commande, id=id)
        nouveau_statut = request.data.get('statut')
        if not nouveau_statut:
            return Response({"message": "Le champ 'statut' est requis."}, status=400)

        if nouveau_statut not in [choice[0] for choice in Commande.STATUT_CHOICE]:
            return Response(
                {"message": "Statut invalide."},
                status=status.HTTP_400_BAD_REQUEST
            )
        commande.statut = nouveau_statut
        commande.save()
        serializer = CommandeSerializer(commande)
        return Response(serializer.data)


# Historique des commandes d’un client (triées par date)
class HistoriqueCommandesClientView(generics.ListAPIView):
    serializer_class = CommandeSerializer

    def get_queryset(self):
        client_id = self.kwargs['id']
        return Commande.objects.filter(client_id=client_id).order_by('-date_commande')


# Détails d’une commande
class DetailCommandeView(generics.RetrieveAPIView):
    queryset = Commande.objects.all()
    serializer_class = CommandeSerializer
    lookup_field = 'id'

# Liste des commandes d'un client 
class CommandesClientView(APIView):
    serializer_class = CommandeSerializer
    
    def get(self, request, id):
        try:
            client = User.objects.get(id=id)
        except User.DoesNotExist:
            return Response({"message": "Client introuvable."}, status=status.HTTP_404_NOT_FOUND)

        commandes = Commande.objects.filter(client=client).order_by('-date_commande')
        serializer = DetailCommandeSerializer(commandes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class StatutsCommandesUtilisateurView(APIView):
    def get(self, request, id):
        try:
            user = User.objects.get(id=id)
            statuts = Commande.objects.filter(client=user).values_list('statut', flat=True)
            return Response({"statuts": list(statuts)}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"message": "Utilisateur introuvable."}, status=status.HTTP_404_NOT_FOUND)