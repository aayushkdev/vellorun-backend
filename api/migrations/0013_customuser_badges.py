# Generated by Django 5.2.1 on 2025-05-19 20:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0012_alter_customuser_email_alter_customuser_username'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='badges',
            field=models.JSONField(blank=True, default=list),
        ),
    ]
