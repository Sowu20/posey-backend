from rest_framework import generics, status
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Avg, Count
from note.models import Note
from users.models import User
from commandes.models import Commande
from note.serializers import NoteSerializer, RegisterNoteSerializer, DetailNoteSerializer, NoteSerializer, TopPrestataireSerializer, CommentaireNoteSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# Enregistrement d’une note avec vérification de double note
class EnregistrerNoteView(generics.CreateAPIView):
    serializer_class = RegisterNoteSerializer
    queryset = Note.objects.all()

class GetNoteView(generics.ListAPIView):
    queryset = Note.objects.all()
    serializer_class = DetailNoteSerializer

    @swagger_auto_schema(
        responses={201: "Liste des notes", 400: "Données invalides"}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
# Liste des notes d’un client donné
class ListeNotesClientView(generics.ListAPIView):
    serializer_class = NoteSerializer

    def get_queryset(self):
        client_id = self.kwargs['id']
        return Note.objects.filter(id=client_id)

# Liste des notes d’une commande donnée
class ListeNotesCommandeView(generics.ListAPIView):
    serializer_class = NoteSerializer

    def get_queryset(self):
        commande_id = self.kwargs['id']
        return Note.objects.filter(id=commande_id)

# Moyenne des notes d’un prestataire donné
class MoyenneNotesPrestataireView(APIView):
    def get(self, request, id):
        commandes = Commande.objects.filter(prestataire__id=id)
        moyenne = Note.objects.filter(commande__in=commandes).aggregate(moyenne_score=Avg('score'))
        return Response({"moyenne": moyenne['moyenne_score']})
    
# Liste des prestataires les mieux notés
class TopPrestatairesAPIView(APIView):
    def get(self, request):
        prestataires = User.objects.filter(
            role='prestataire', 
            prestataire_notes__isnull=False
        ).annotate(
            moyenne_notes=Avg('prestataire_notes__score'),
            nombre_notes=Count('prestataire_notes')
        ).filter(
            nombre_notes__gte=3  
        ).order_by('-moyenne_notes')[:3] 

        serializer = TopPrestataireSerializer(prestataires, many=True)
        return Response(serializer.data)
    
# Liste des prestataires avec un score
class PrestataireScoreView(APIView):
    def get(self, request):
        scores = (
            Note.objects
            .values('prestataire__id', 'prestataire__nom', 'prestataire__prenom')
            .annotate(moyenne_score=Avg('score'))
            .order_by('-moyenne_score')
        )
        return Response(scores, status=status.HTTP_200_OK)
    
class MoyenneNotePrestataireView(APIView):
    def get(self, request, id):
        notes = Note.objects.filter(prestataire__id=id)
        if not notes.exists():
            return Response({'moyenne_score': 0})
        moyenne = notes.aggregate(Avg('score'))['score__avg']
        return Response({'moyenne_score': moyenne})
    
class CommentairesPrestataireView(ListAPIView):
    serializer_class = CommentaireNoteSerializer

    def get_queryset(self):
        id = self.kwargs['prestataire_id']
        return Note.objects.filter(prestataire_id=id, commentaire__isnull=False).exclude(commentaire="").order_by('-id')