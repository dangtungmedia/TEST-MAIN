# Generated by Django 5.0.6 on 2024-08-02 13:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('render', '0008_videorender_url_text_video'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='videorender',
            name='url_text_video',
        ),
    ]
