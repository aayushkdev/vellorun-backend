# Generated by Django 5.2.1 on 2025-05-19 18:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0010_customuser_online_alter_customuser_avatar'),
    ]

    operations = [
        migrations.AddField(
            model_name='place',
            name='category',
            field=models.CharField(default='campus', max_length=69),
        ),
        migrations.AlterField(
            model_name='place',
            name='level',
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='place',
            name='xp_reward',
            field=models.IntegerField(default=20),
        ),
    ]
