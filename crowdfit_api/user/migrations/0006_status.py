# Generated by Django 2.1.7 on 2019-03-16 15:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0005_household'),
    ]

    operations = [
        migrations.CreateModel(
            name='Status',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('desc', models.CharField(max_length=256, null=True)),
                ('createDate', models.DateTimeField(auto_now=True)),
                ('lastUpdate', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
