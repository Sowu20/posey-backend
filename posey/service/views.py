from django.shortcuts import render
from rest_framework import generics, permissions
from .models import Service
from .serilizers import ServiceSerializer

# Liste et création des services d'un prestataire
class ServiceListCreateView(generics.ListCreateAPIView):
    serializer_class = ServiceSerializer
    # permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Service.objects.filter(prestataire=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(prestataire=self.request.user)

# Liste des services d'un prestataire
class ServiceDetailView(generics.ListAPIView):
    serializer_class = ServiceSerializer
    def get_queryset(self):
        prestataire_id = self.kwargs.get("id")
        return Service.objects.filter(prestataire_id=prestataire_id).order_by("-date_creation")