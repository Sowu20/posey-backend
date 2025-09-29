from django.shortcuts import render
from rest_framework import generics, permissions
from .models import Service
from .serilizers import ServiceSerializer

# Liste et création des services d'un prestataire
class ServiceListCreateView(generics.ListCreateAPIView):
    serializer_class = ServiceSerializer
    # permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        prestataire_id = self.kwargs['prestataire_id']
        return Service.objects.filter(prestataire_id=prestataire_id)
    
    def perform_create(self, serializer):
        serializer.save(prestataire=self.request.user)

# Détail, modification, suppresion d'un service
class ServiceDetailView(generics.ListAPIView):
    # queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    # permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        prestataire_id = self.kwargs.get("id")
        return Service.objects.filter(prestataire_id=prestataire_id).order_by("-date_creation")