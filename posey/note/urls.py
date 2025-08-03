from django.urls import path
from note.views import PrestataireScoreView, MoyenneNotePrestataireView, EnregistrerNoteView, GetNoteView, ListeNotesClientView, ListeNotesCommandeView, MoyenneNotesPrestataireView, TopPrestatairesAPIView, CommentairesPrestataireView

urlpatterns = [
    path('register/', EnregistrerNoteView.as_view(), name='note-create'),
    path('get/', GetNoteView.as_view(), name='note-list'),
    path('liste_notes_client/<int:id>/', ListeNotesClientView.as_view()),
    path('liste_notes_commande/<int:id>/', ListeNotesCommandeView.as_view()),
    path('moyenne_note/<int:id>/moyenne/', MoyenneNotesPrestataireView.as_view()),
    path('prestataires/top-notes/', TopPrestatairesAPIView.as_view(), name='top_prestataires'),
    path('prestataire-scores/', PrestataireScoreView.as_view(), name='prestataire-scores'),
    path('prestataire-note/<int:id>/', MoyenneNotePrestataireView.as_view(), name='moyenne-note-prestataire'),
    path('commentaires/<int:id>/', CommentairesPrestataireView.as_view()),
]