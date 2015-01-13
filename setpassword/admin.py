from django.contrib import admin
from . import models

class TokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'allow_reset')

admin.site.register(models.Token, TokenAdmin)
