from django import forms
from django.contrib.auth import models as auth_models
import shortuuid
from django.utils.html import format_html
from . import models

class LoginTokenWidget(forms.Widget):
    def render(self, name, value, attrs=None):
        uid = shortuuid.uuid()
        return format_html(
            '<input type=hidden name="{}_token" value="{}">'
            '<input type=text disabled value="{}" class=vTextField><br>'
            '<input type=checkbox name="{}_enabled" id="{}_enabled">'
            '<label for="{}_enabled">Use this token</label>',
            name, uid, uid, name, name, name)

    def value_from_datadict(self, data, files, name):
        if data.get(name + '_enabled'):
            return data.get(name + '_token')
        else:
            return None

class LoginTokenField(forms.Field):
    widget = LoginTokenWidget

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("required", False)
        super(LoginTokenField, self).__init__(*args, **kwargs)

class SetPasswordUserCreationForm(forms.ModelForm):
    class Meta:
        model = auth_models.User
        fields = ("username",)

    token = LoginTokenField()

    def save(self, commit=True):
        user = super(SetPasswordUserCreationForm, self).save(commit=True)
        token = self.cleaned_data.get('token')
        if token:
            models.Token(user=user, token=token).save()
        return user

    def save_m2m(self):
        pass
