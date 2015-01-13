from django.db import models
from django.contrib.auth import models as auth_models
import shortuuid

def uuid():
    return shortuuid.uuid()

class Token(models.Model):
    user = models.ForeignKey(auth_models.User)
    token = models.CharField(max_length=255, default=uuid)
    allow_reset = models.BooleanField(default=False)
