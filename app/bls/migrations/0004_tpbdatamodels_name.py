# Generated by Django 3.1.3 on 2023-12-25 19:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bls', '0003_tpbdatamodels'),
    ]

    operations = [
        migrations.AddField(
            model_name='tpbdatamodels',
            name='name',
            field=models.TextField(default=55),
            preserve_default=False,
        ),
    ]