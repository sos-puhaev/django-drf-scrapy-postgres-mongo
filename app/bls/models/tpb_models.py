from django.db import models

class TpbDataModels(models.Model):
    start_page = models.TextField()
    end_page = models.TextField()
    url_parse = models.TextField()
    start_url = models.TextField()
    timer = models.TextField()
    name = models.TextField()
    auto_scraper = models.TextField()

    class Meta:
        db_table = 'settings_tpb'