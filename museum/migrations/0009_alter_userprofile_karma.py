# Generated by Django 3.2.9 on 2021-11-28 11:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('museum', '0008_meme_meme_lord'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='karma',
            field=models.IntegerField(default=0),
        ),
    ]
