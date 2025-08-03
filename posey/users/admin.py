from django.contrib import admin
from users.models import User

# Register your models here.
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'nom', 'prenom', 'email', 'role', 'quartier', 'ville', 'categorie')

admin.site.register(User, UserAdmin)