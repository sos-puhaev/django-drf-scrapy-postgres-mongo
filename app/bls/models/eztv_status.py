from django.db import models

class EztvStatus(models.Model):
    status = models.TextField()

    class Meta:
        db_table = "eztv_status"