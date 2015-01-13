from django.contrib import admin
from . import models

class PosixUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'shell')

admin.site.register(models.PosixUser, PosixUserAdmin)
