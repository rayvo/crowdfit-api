# Generated by Django 2.1.7 on 2019-03-16 14:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0003_address'),
    ]

    operations = [
        migrations.CreateModel(
            name='Apt',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('desc', models.CharField(max_length=500, null=True)),
                ('createDate', models.DateTimeField(auto_now=True)),
                ('lastUpdate', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.AlterField(
            model_name='address',
            name='city',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cities', to='user.City'),
        ),
        migrations.AddField(
            model_name='apt',
            name='address',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='addresses', to='user.Address'),
        ),
    ]