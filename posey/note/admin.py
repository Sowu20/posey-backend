from django.contrib import admin
from note.models import Note

# Register your models here.
class NoteAdmin(admin.ModelAdmin):
    list_display = ('client', 'prestataire', 'commande', 'score')

admin.site.register(Note, NoteAdmin)