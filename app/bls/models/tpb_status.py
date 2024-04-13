from django.db import models

class TpbStatus(models.Model):
    status = models.TextField()

    class Meta:
        db_table = "tpb_status"