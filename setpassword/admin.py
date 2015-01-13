from django.contrib import admin
from . import models, forms
from django.contrib.auth import admin as auth_admin

class TokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'allow_reset')

admin.site.register(models.Token, TokenAdmin)

auth_admin.UserAdmin.add_form = forms.SetPasswordUserCreationForm
auth_admin.UserAdmin.add_fieldsets = (
    (None, {
        'classes': ('wide',),
        'fields': ('username', 'token'),
    }),
)
