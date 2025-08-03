from django.urls import path
from users.views import PrestataireListView, PrestataireDetailView, UserDetailByIdView, LoginAPIView, RegisterView, UpdateView, GetView, DeleteView, UsersByLocationView, UsersByQuartierView, UsersByVilleView, UsersByRoleView, PrestatairesAvecCategorieView, ListePrestataireParCategorieView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('update/<int:id>/', UpdateView.as_view(), name='update'),
    path('detail/', GetView.as_view(), name='detail'),
    path('delete/<int:id>/', DeleteView.as_view(), name='delete'),
    path('location/', UsersByLocationView.as_view(), name='users_by_location'),
    path('quartier/', UsersByQuartierView.as_view(), name='users_by_quartier'),
    path('ville/', UsersByVilleView.as_view(), name='users_by_ville'),
    path('role/', UsersByRoleView.as_view(), name='users_by_role'),
    path('prestataires/', PrestatairesAvecCategorieView.as_view(), name='prestataires-avec-categorie'),
    path('categorie/', ListePrestataireParCategorieView.as_view(), name='prestataires-par-categorie'),
    path('prestataires/', PrestataireListView.as_view(), name='prestataire-list'),
    path('<int:id>/', UserDetailByIdView.as_view(), name='user-detail-by-id'),
    path('prestataires/<int:id>/', PrestataireDetailView.as_view(), name='prestataire-detail'),
]