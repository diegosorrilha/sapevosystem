# Generated by Django 2.1 on 2019-09-02 14:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='projeto',
            name='avaliado',
            field=models.BooleanField(default=False, null=True),
        ),
    ]
