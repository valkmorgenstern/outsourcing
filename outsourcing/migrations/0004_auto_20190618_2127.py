# Generated by Django 2.2.2 on 2019-06-18 21:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('outsourcing', '0003_auto_20190612_1432'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='organization',
            name='inn',
        ),
        migrations.AddField(
            model_name='organization',
            name='itn',
            field=models.CharField(default=1, max_length=16),
            preserve_default=False,
        ),
    ]
