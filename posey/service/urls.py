from django.urls import path
from .views import ServiceListCreateView, RegisterServiceView, ServiceDetailView, UpdateServiceView, DeleteServiceView

urlpatterns = [
    path('mes_services/<int:prestataire_id>', ServiceListCreateView.as_view(), name='service-list-create'),
    path('register_service/', RegisterServiceView.as_view(), name='register-service'),
    path('list_service/<int:id>/', ServiceDetailView.as_view(), name='service-detail'),
    path('update_service/<int:id>/', UpdateServiceView.as_view(), name='update-service'),
    path('delete_service/<int:id>/', DeleteServiceView.as_view(), name='delete-service')
]