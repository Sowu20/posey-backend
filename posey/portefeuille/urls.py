from django.urls import path
from portefeuille.views import FairePaiementView, VerifierPaiementView, VerifierTransactionView, TransactionsUtilisateurView, VerifierPaiementView, ConsulterSoldeView, ListeTransactionView, ListeTransactionStatutView, PayGateWebhookView

urlpatterns = [
    path('solde/<int:id>/', ConsulterSoldeView.as_view()),
    path('recharge/', FairePaiementView.as_view(), name='faire-paiement'),
    path('verifier-paiement/', VerifierPaiementView.as_view(), name='verifier-paiement'),
    path('verifier-transaction/', VerifierTransactionView.as_view(), name='verifier-transaction'),
    path('liste_transaction/', ListeTransactionView.as_view()),
    path('liste_transaction/statut/', ListeTransactionStatutView.as_view()),
    path('transactions/<int:id>/', TransactionsUtilisateurView.as_view(), name='transactions-utilisateur'),
    path('consulter-solde/<int:id>/',ConsulterSoldeView.as_view(), name='consulter-solde'),
    path('transactions/<int:id>/', TransactionsUtilisateurView.as_view(), name='transactions-utilisateur'),
    path('webhook/', PayGateWebhookView.as_view(), name='paygate-webhook'),
]