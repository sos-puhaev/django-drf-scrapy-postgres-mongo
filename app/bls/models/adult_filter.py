from django.db import models

class AdultFilterModel(models.Model):

    check = models.TextField()
    word = models.TextField()

    class Meta:
        db_table = "adult_filter"