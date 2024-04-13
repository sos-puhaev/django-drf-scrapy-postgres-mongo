from django.db import models

class PosgresDataModels(models.Model):

    name = models.TextField()
    email = models.TextField()
    data_comment = models.TextField()
    comments = models.TextField()
    id_torrent = models.TextField()
    audio = models.IntegerField(null=True, blank=True)
    video = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'bls_scrapy'