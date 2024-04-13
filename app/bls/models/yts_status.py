from django.db import models

class YtsStatus(models.Model):
    status = models.TextField()

    class Meta:
        db_table = "yts_status"