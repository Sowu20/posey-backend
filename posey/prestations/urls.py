from django.urls import path
from prestations.views import RegisterCategorieView, SupprimerNotificationView, PrestationClientView, PrestationRefusesView, PrestatairesNonValidesView, ValiderPrestataireView, PrestationsEnAttenteView, DemandePrestationView, RegisterPrestationView, UpdateCategorieView, PrestationsTermineesParPrestataire, UpdatePrestationView, GetCategorieView, GetPrestationView, DeleteCategorieView, DeletePrestationView, PrestataireView, AccepterPrestationView, PrestationsDisponibesParCategorie, PrestationsDisponiblesView, PrestataireAvisView, PrestataireNoteView, PrestatairePrestationsView, PrestataireStatsView, DemandeCibleeCreateView, DemandesRecuesView, RefuserPrestationView, NotificationListView, EnvoyerDemandeCibleeView, RepondreDemandeCibleeView, ListeNotificationsView, MarquerNotificationCommeLue, MarquerTousLue, PrestationsAvecPrixListView

urlpatterns = [
    # Catégorie
    path('register_categorie/', RegisterCategorieView.as_view(), name="register_categorie"),
    path('update_categorie/<int:id>/', UpdateCategorieView.as_view(), name="update_categorie"),
    path('detail_categorie/', GetCategorieView.as_view(), name='detail_categorie'),
    path('delete_categorie/<int:id>/', DeleteCategorieView.as_view(), name="delete_categorie"),
    path('prestataires/non_valides/', PrestatairesNonValidesView.as_view()),
    path('valider_prestataire/<int:id>/', ValiderPrestataireView.as_view()),
    # Prestation
    path('register_prestation/', RegisterPrestationView.as_view(), name="register_prestation"),
    path('update_prestation/<int:id>/', UpdatePrestationView.as_view(), name="update_prestation"),
    path('detail_prestation/', GetPrestationView.as_view(), name='detail_prestation'),
    path('delete_prestation/<int:id>/', DeletePrestationView.as_view(), name="delete_prestation"),
    path('client/<int:id>/', PrestationClientView.as_view(), name='prestation-client'),

    path('demandes/', DemandePrestationView.as_view(), name='creer-prestation'),
    path('prestataire/<int:id>/', PrestataireView.as_view(), name='prestataire'),
    path('accepter/<int:id>/', AccepterPrestationView.as_view(), name='accepter-prestation'),
    path('prestations_disponibles/', PrestationsDisponibesParCategorie.as_view(), name='prestations_disponibles'),
    path('notifications/', NotificationListView.as_view(), name='notifications'),

    path('disponibles/', PrestationsDisponiblesView.as_view()),
    path('services/<int:id>/', PrestatairePrestationsView.as_view(), name='liste_prestations'),
    path('stats/<int:id>/', PrestataireStatsView.as_view(), name='stats'),
    path('note/<int:id>/',PrestataireNoteView.as_view(), name='note'),
    path('avis/<int:id>/', PrestataireAvisView.as_view(), name='avis'),
    path('en_attente/', PrestationsEnAttenteView.as_view(), name='prestations-en-attente'),
    path('demande-ciblee/', DemandeCibleeCreateView.as_view(), name='demande-ciblee-create'),
    path('recues/<int:id>/', DemandesRecuesView.as_view(), name='demandes_recues'),
    path('refuses/<int:id>/', PrestationRefusesView.as_view(), name='prestations-refuses'),
    path('refuser_prestation/<int:id>/',RefuserPrestationView.as_view(), name='refuser_prestation'),

    path('refusees/toutes/', PrestationRefusesView.as_view(), name='prestations-refusees-par-prestataire'),
    path('terminees/<int:id>/', PrestationsTermineesParPrestataire.as_view()),
    path('envoyer-demande/', EnvoyerDemandeCibleeView.as_view()),
    path('repondre-demande/<int:id>/', RepondreDemandeCibleeView.as_view()),
    path('notifications/', ListeNotificationsView.as_view()),
    path('notifications/lue/<int:id>/', MarquerNotificationCommeLue.as_view()),
    path('notifications/tous_lues/', MarquerTousLue.as_view()),
    path('notifications/supprimer/<int:id>/', SupprimerNotificationView.as_view()),
    path('prestations_avec_prix/', PrestationsAvecPrixListView.as_view()),
]