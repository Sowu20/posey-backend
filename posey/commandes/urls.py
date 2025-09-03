from django.urls import path
from commandes.views import RegisterCommandeView, StatutsCommandesUtilisateurView, CommandesClientView, UpdateCommandeView, DeleteCommandeView, GetCommandeView, CommandesParClientView, CommandesParStatutView, ChangerStatutCommandeView, HistoriqueCommandesClientView, DetailCommandeView, MesCommandesView, PrestationsDisponibleView, AccepterCommandeView, RefuserCommandeView, CreerCommandeView

urlpatterns = [
    path('register_commande/', RegisterCommandeView.as_view(), name="register_categorie"),
    path('update_commande/<int:id>/', UpdateCommandeView.as_view(), name="update_categorie"),
    path('detail_commande/', GetCommandeView.as_view(), name='detail_categorie'),
    path('delete_commande/<int:id>/', DeleteCommandeView.as_view(), name="delete_categorie"),
    path('liste_client/<int:id>/', CommandesParClientView.as_view()),
    path('liste_statut/', CommandesParStatutView.as_view()),
    path('<int:id>/changer_statut/', ChangerStatutCommandeView.as_view()),
    path('historique_commande/<int:id>/historique/', HistoriqueCommandesClientView.as_view()),
    path('client/<int:id>/', CommandesClientView.as_view(), name='commandes-client'),
    path('<int:id>/', DetailCommandeView.as_view()),
    path('statut/<int:id>/', StatutsCommandesUtilisateurView.as_view(), name='statuts-commandes-utilisateur'),
    path('mes_commandes/', MesCommandesView.as_view(), name='mes-commandes'),
    path('prestations_disponibles/', PrestationsDisponibleView.as_view(), name='prestations-disponibles'),
    path('<int:id>/accepter/', AccepterCommandeView.as_view(), name='accepter-commande'),
    path('<int:id>/refuser/', RefuserCommandeView.as_view(), name='refuser-commande'),
    path('creer_commande/', CreerCommandeView.as_view(), name="creer_commande"),
]