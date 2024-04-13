from django.db import models

class YtsDataModels(models.Model):
    limit = models.TextField()
    offset = models.TextField()
    url_parse = models.TextField()
    allowed_domains = models.TextField()
    timer = models.TextField()
    name = models.TextField()
    auto_scraper = models.TextField()

    class Meta:
        db_table = 'settings_yts'