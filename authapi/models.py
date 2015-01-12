from django.db import models
import shortuuid

def uuid():
    return shortuuid.uuid()

class APIKey(models.Model):
    key = models.CharField(max_length=255, default=uuid)
    description = models.CharField(max_length=255)

    def __unicode__(self):
        return self.description
