from django.shortcuts import render
from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Service
from .serilizers import ServiceSerializer

# Liste et création des services d'un prestataire
class ServiceListCreateView(generics.ListCreateAPIView):
    serializer_class = ServiceSerializer

    def get_queryset(self):
        prestataire_id = self.kwargs.get('prestataire_id')
        if prestataire_id:
            return Service.objects.filter(prestataire_id=prestataire_id)
        return Service.objects.filter(prestataire=self.request.user)

    def perform_create(self, serializer):
        serializer.save(prestataire=self.request.user)

# Enregistrer un service
class RegisterServiceView(generics.CreateAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer 

# Liste des services d'un prestataire
class ServiceDetailView(generics.ListAPIView):
    serializer_class = ServiceSerializer
    def get_queryset(self):
        prestataire_id = self.kwargs.get("id")
        return Service.objects.filter(prestataire_id=prestataire_id).order_by("-date_creation")
    
# Modifier un service
class UpdateServiceView(generics.UpdateAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer 
    lookup_field = 'id'

# Supprimer un service
class DeleteServiceView(APIView):
    def delete(self, request, id, *args, **kwargs):
        try:
            service = Service.objects.get(id=id)
            service.delete()
            return Response({"Utilisateur supprimé avec succès."}, status=204)
        except Service.DoesNotExist:
            return Response({"Utilisateur introuvable."}, status=400)