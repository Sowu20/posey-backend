from django.urls import path
from .views import ServiceListCreateView, ServiceDetailView

urlpatterns = [
    path('prestataire/<int:prestataire_id>/', ServiceDetailView.as_view(), name='service-list-create'),
    path('<int:pk>/', ServiceListCreateView.as_view(), name='service-detail')
]