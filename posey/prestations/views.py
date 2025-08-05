from rest_framework import viewsets, generics
from users.permissions import IsAdmin, IsClient, IsPrestataire
from prestations.models import CategoriePrestation, Notification, Prestation, DemandeCiblee
from prestations.serializers import NotificationSerializer, PrestationClientSerializer, RegisterCategorieSerializer, RegisterPrestationSerializer, UpdateCategorieSerializer, UpdatePrestationSerializer, DetailCategorieSerializer, DetailPrestationSerializer, ListePrestataireSerializer, PrestationSerializer, NoteSerializer, PrestationDisponibleSerializer, DemandeCibleeSerializer, PrestationRefuseeSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework import status, serializers
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.shortcuts import get_object_or_404
from django.db import transaction, models
from django.utils import timezone
from users.models import User
from note.models import Note

# Catégorie
class RegisterCategorieView(generics.CreateAPIView):
    queryset = CategoriePrestation.objects.all()
    serializer_class = RegisterCategorieSerializer
    
    @swagger_auto_schema(
        operation_description="Créer une nouvelle catégorie.",
        responses={201: "Catégorie créé avec succès", 400: "Données invalides"}
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
    
class UpdateCategorieView(generics.UpdateAPIView):
    queryset = CategoriePrestation.objects.all()
    serializer_class = UpdateCategorieSerializer
    lookup_field = 'id'

    @swagger_auto_schema(
        operation_description="Modifier une catégorie.",
        responses={201: "Catégorie modifié avec succès", 400: "Données non modifié"}
    )
    def put(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
class GetCategorieView(generics.ListAPIView):
    queryset = CategoriePrestation.objects.all()
    serializer_class = DetailCategorieSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        responses={201: "Liste des catégories", 400: "Données invalides"}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
class DeleteCategorieView(APIView):
    def delete(self, request, id, *args, **kwargs):
        try:
            categorie = CategoriePrestation.objects.get(id=id)
            categorie.delete()
            return Response({"Catégorie supprimé avec succès."}, status=204)
        except CategoriePrestation.DoesNotExist:
            return Response({"Catégorie introuvable."}, status=400)
        
# Prestation
class RegisterPrestationView(generics.CreateAPIView):
    queryset = Prestation.objects.all()
    serializer_class = RegisterPrestationSerializer
    
    @swagger_auto_schema(
        operation_description="Créer une prestation.",
        responses={201: "Prestation créé avec succès", 400: "Données invalides"}
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
    
class UpdatePrestationView(generics.UpdateAPIView):
    queryset = Prestation.objects.all()
    serializer_class = UpdatePrestationSerializer
    lookup_field = 'id'

    @swagger_auto_schema(
        operation_description="Modifier une prestation.",
        responses={201: "Prestation modifié avec succès", 400: "Données non modifié"}
    )
    def put(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
class GetPrestationView(generics.ListAPIView):
    queryset = Prestation.objects.all()
    serializer_class = DetailPrestationSerializer

    @swagger_auto_schema(
        responses={201: "Liste des prestations", 400: "Données invalides"}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
class DeletePrestationView(APIView):
    def delete(self, request, id, *args, **kwargs):
        try:
            prestation = Prestation.objects.get(id=id)
            prestation.delete()
            return Response({"Prestation supprimée avec succès."}, status=204)
        except Prestation.DoesNotExist:
            return Response({"Prestation introuvable."}, status=400)

class DemandePrestationView(generics.CreateAPIView):
    queryset = Prestation.objects.all()
    serializer_class = PrestationSerializer

    def create(self, request, *args, **kwargs):
        data = request.data.copy()

        if request.user.is_authenticated:
            data['client'] = request.user.id
        elif not data.get('client'):
            return Response(
                {'error': 'Le client doit être spécifié ou vous devez être connecté.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
class demanderPerstationView(APIView):
    def post(self, request):
        serializer = PrestationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# Avoir les prestations du prestataire
class PrestataireView(APIView):
    def get(self, request, id):
        try:
            # Utiliser le paramètre id de l'URL
            prestataire_id = id
            
            # Optionnel : vérifier que le prestataire existe
            prestataire = get_object_or_404(User, id=prestataire_id)
            
            # Filtrer les prestations avec l'ID du paramètre
            prestations = Prestation.objects.filter(prestataire=prestataire_id)
            prestations_serialized = PrestationSerializer(prestations, many=True).data
            
            # Calculer les statistiques
            total_prestations = prestations.count()
            prestations_en_attente = prestations.filter(statut='en_attente').count()
            
            # Récupérer les notes
            notes = Note.objects.filter(prestataire=prestataire_id)
            total_avis = notes.count()
            
            return Response({
                "prestations": prestations_serialized,
                "total_prestations": total_prestations,
                "prestations_en_attente": prestations_en_attente,
                "note": notes.values(),  # Sérialiser les notes
                "total_avis": total_avis,
            })
            
        except Exception as e:
            return Response(
                {"error": f"Erreur lors de la récupération des données: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# Accepter les prestations
class AccepterPrestationView(APIView):
    def post(self, request, id):
        try:
            prestation = Prestation.objects.get(id=id)
            if prestation.accepte(request.user):
                Notification.objects.create(
                    user=prestation.client,
                    message=f"Votre demande de prestation « {prestation.titre} » a été acceptée par {request.user.username}."
                )
                return Response({'message': 'Prestation acceptée'}, status=200)
            else:
                return Response({'error': 'Impossible d\'accepter cette prestation.'}, status=400)
        except Prestation.DoesNotExist:
            return Response({'error': 'Prestation introuvable'}, status=404)
        
# Avoir les prestations disponibles par catégorie
class PrestationsDisponibesParCategorie(APIView):
    def get(self, request):
        prestation = Prestation.objects.filter(prestataire__isnull=True)
        serializer = PrestationDisponibleSerializer(prestation, many=True)
        return Response(serializer.data)
    
# Prestations disponibles
class PrestationsDisponiblesView(APIView):
    def get(self, request):
        prestations = Prestation.objects.filter(
            statut='en_attente',
            prestataire__isnull=True
        )
        serializer = PrestationSerializer(prestations, many=True)
        return Response(serializer.data)
    
# Prestations du prestataire
class PrestatairePrestationsView(APIView):
    def get(self, request, id):
        prestataire = get_object_or_404(User, id=id)
        prestations = Prestation.objects.filter(
            prestataire=prestataire,
            statut='en attente',
            prestataire__isnull=True
        )
        serializer = PrestationSerializer(prestations, many=True)
        return Response(serializer.data)

# Stattistiques des prestations(Total des prestations et en attente)
class PrestataireStatsView(APIView):
    def get(self, request, id):
        prestataire = get_object_or_404(User, id=id)
        prestations = Prestation.objects.filter(prestataire=prestataire)
        total_prestations = prestations.count()
        prestations_en_attente = prestations.filter(statut='en_attente').count()

        return Response({
            "total_prestations": total_prestations,
            "prestations_en_attente": prestations_en_attente
        })

# Note moyenne du prestataire
class PrestataireNoteView(APIView):
    def get(self, request, id):
        prestataire = get_object_or_404(User, id=id)
        notes = Note.objects.filter(prestataire=prestataire)

        if notes.exists():
            moyenne_score = round(notes.aggregate(models.Avg("score"))["score__avg"], 1)
        else:
            moyenne_score = 0.0

        return Response({
            "moyenne_score": moyenne_score
        })

# Liste et Total des avis:
class PrestataireAvisView(APIView):

    def get(self, request, id):
        prestataire = get_object_or_404(User, id=id)
        notes = Note.objects.filter(prestataire=prestataire)
        serializer = NoteSerializer(notes, many=True)

        return Response({
            "total_avis": notes.count(),
            "avis": serializer.data
        })
    
class PrestationsEnAttenteView(APIView):
    def get(self, request):
        try:
            # Récupérer uniquement les prestations en attente et non assignées
            prestations = Prestation.objects.filter(
                statut='en_attente',
                prestataire__isnull=True
            ).order_by('-date_creation')
            
            # Sérialiser les données
            serializer = PrestationSerializer(prestations, many=True)
            
            return Response({
                'prestations': serializer.data,
                'count': prestations.count()
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            # Pour debug - vous verrez l'erreur dans la console Django
            print(f"Erreur dans PrestationsEnAttenteView: {e}")
            import traceback
            traceback.print_exc()
            
            return Response({
                'error': 'Erreur lors du chargement des prestations en attente.',
                'details': str(e)  # Temporaire pour debug
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class DemandeCibleeCreateView(generics.CreateAPIView):
    queryset = DemandeCiblee.objects.all()
    serializer_class = DemandeCibleeSerializer

class EnvoyerDemandeCibleeView(APIView):
    def post(self, request):
        prestation_id = request.data.get('prestation')
        prestataire_id = request.data.get('prestataire')
        try:
            prestation = Prestation.objects.get(id=prestation_id, client=request.user)
            prestataire = User.objects.get(id=prestataire_id, role='prestataire')
        except Prestation.DoesNotExist:
            return Response({'error': 'Prestation non trouvée.'}, status=404)
        except User.DoesNotExist:
            return Response({'error': 'Prestataire non trouvé.'}, status=404)
        
        if DemandeCiblee.objects.filter(prestation=prestation, prestataire=prestataire).exists():
            return Response({'error': 'Demande déjà envoyée.'}, status=400)
        
        demande = DemandeCiblee.objects.create(prestation=prestation, prestataire=prestataire)

        Notification.objects.create(
            utilisateur=prestataire,
            message=f"Vous avez reçu une demande pour la prestation : '{prestation.titre}'"
        )
        serializer = DemandeCibleeSerializer(demande)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
class RepondreDemandeCibleeView(APIView):
    def post(self, request, id):
        try:
            demande = DemandeCiblee.objects.get(id=id, prestataire=request.user)
        except DemandeCiblee.DoesNotExist:
            return Response({"error": "Demande introuvable ou non autorisée."}, status=status.HTTP_404_NOT_FOUND)

        etat = request.data.get("etat")
        if etat not in ["acceptee", "refusee"]:
            return Response({"error": "État invalide."}, status=status.HTTP_400_BAD_REQUEST)
        
        Notification.objects.create(
            utilisateur=demande.prestation.client,
            message=f"Votre demande pour '{demande.prestation.titre}' a été {etat} par le prestataire {request.user.username}"
        )

        demande.etat = etat
        demande.save()

        return Response({"message": f"Demande {etat} avec succès."})
    
# Récupérer les notifications
class ListeNotificationsView(ListAPIView):
    serializer_class = NotificationSerializer

    def get_queryset(self):
        return Notification.objects.filter(utilisateur=self.request.user).order_by('-date')
    
# Marquer les messages comme lus
class MarquerNotificationCommeLue(APIView):
    # permission_classes = [IsAuthenticated]

    def post(self, request, id):
        notif = Notification.objects.filter(id=id, utilisateur=request.user).first()
        if notif:
            notif.lu = True
            notif.save()
            return Response({"message": "Notification marquée comme lue"})
        return Response({"error": "Notification introuvable"}, status=404)

class DemandesRecuesView(APIView):
    def get(self, request, id):
        try:
            demandes = DemandeCiblee.objects.filter(
                prestataire_id=id,
                est_acceptee=False,
                est_refusee=False
            ).select_related("prestation", "prestation__client")

            data = [
                {
                    "demande_id": d.id,
                    "prestation_id": d.prestation.id,
                    "titre": d.prestation.titre,
                    "description": d.prestation.description,
                    "statut": d.prestation.statut,
                    "date_demande": d.prestation.date_demande,
                    "client": f"{d.prestation.client.prenom} {d.prestation.client.nom}"
                }
                for d in demandes
            ]
            return Response(data)
        except Exception as e:
            return Response({"error": str(e)}, status=500)
        
class PrestationRefusesView(APIView):
    def get(self, request):
        prestations = Prestation.objects.filter(statut='refusee')
        serializer = PrestationSerializer(prestations, many=True)

        return Response(serializer.data)
    
class RefuserPrestationView(APIView):
    def post(self, request, id):
        try:
            prestation = Prestation.objects.get(id=id)
            prestation.prestataire = None
            prestation.statut = 'refusee'
            prestation.save()

            return Response({'message': 'La prestation a été refusée avec succès.'})
        except Prestation.DoesNotExist:
            return Response({'error': 'Prestation non trouvée.'}, status=404)
        
class NotificationListView(APIView):
    def get(self, request):
        user_id = request.query_params.get('user_id')
        if not user_id or str(request.user.id) != user_id:
            return Response({'error': "Non autorisé"}, status=403)

        notifications = Notification.objects.filter(user_id=user_id).order_by('-created_at')
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)

class PrestationClientView(APIView):
    def get(self, request, id):
        prestations = Prestation.objects.filter(client_id=id).order_by('-date_demande')
        serializer = PrestationClientSerializer(prestations, many=True)
        return Response(serializer.data)

# Avoir le nombre de prestataire terminées par un prestataire
class PrestationsTermineesParPrestataire(APIView):
    def get(self, request, id):
        total = Prestation.objects.filter(prestataire_id=id, statut='terminee').count()
        return Response({"total": total})