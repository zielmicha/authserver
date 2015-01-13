# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import annoying.fields


class Migration(migrations.Migration):

    dependencies = [
        ('posixuser', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='posixuser',
            name='id',
        ),
        migrations.AlterField(
            model_name='posixuser',
            name='user',
            field=annoying.fields.AutoOneToOneField(related_name='posix_user', primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
