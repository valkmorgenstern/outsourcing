# Generated by Django 2.2.2 on 2019-06-18 23:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('outsourcing', '0005_order_category'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30, unique=True)),
            ],
        ),
        migrations.AddField(
            model_name='order',
            name='tags',
            field=models.ManyToManyField(related_name='orders', to='outsourcing.Tag'),
        ),
    ]
