# Generated by Django 5.0.6 on 2024-08-02 20:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0004_remove_profilechannel_channel_voice'),
    ]

    operations = [
        migrations.AddField(
            model_name='profilechannel',
            name='is_content',
            field=models.BooleanField(default=True),
        ),
    ]
