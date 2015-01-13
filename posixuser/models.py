from django.db import models
from django.contrib.auth import models as auth_models
from django.conf import settings
from annoying.fields import AutoOneToOneField

class PosixUser(models.Model):
    user = AutoOneToOneField(auth_models.User, related_name='posix_user', primary_key=True)
    shell = models.CharField(max_length=255, default=settings.DEFAULT_SHELL)

    def __unicode__(self):
        return 'Posix %s' % self.user
