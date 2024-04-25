from django.db import models


class TimeStamp(models.Model):
    """ TimeStamp Model inherited by all models in the project"""

    created_at = models.DateTimeField('created at', auto_now_add=True)
    updated_at = models.DateTimeField('updated at', auto_now=True)

    class Meta:
        abstract = True