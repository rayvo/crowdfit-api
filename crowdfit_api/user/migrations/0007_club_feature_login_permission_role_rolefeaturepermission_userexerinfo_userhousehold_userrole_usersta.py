# Generated by Django 2.1.7 on 2019-03-20 08:36

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0006_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='Club',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=125, unique=True)),
                ('phone', models.CharField(max_length=11)),
                ('clubRegNum', models.CharField(max_length=10)),
                ('clubRegDate', models.DateTimeField()),
                ('otNum', models.IntegerField()),
                ('otPeriod', models.IntegerField()),
                ('desc', models.TextField()),
                ('createDate', models.DateTimeField(auto_now=True)),
                ('lastUpdate', models.DateTimeField(auto_now_add=True)),
                ('address', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='address_club_list', to='user.Address')),
                ('apt', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='apt_club_list', to='user.Apt')),
            ],
        ),
        migrations.CreateModel(
            name='Feature',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('desc', models.TextField(null=True)),
                ('createDate', models.DateTimeField(auto_now=True)),
                ('lastUpdate', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Login',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('loginTime', models.DateTimeField()),
                ('logoutTime', models.DateTimeField()),
                ('isLast', models.BooleanField(default=False)),
                ('createDate', models.DateTimeField(auto_now=True)),
                ('lastUpdate', models.DateTimeField(auto_now_add=True)),
                ('lastFeature', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='feature_login_list', to='user.Feature')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_login_list', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Permission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('desc', models.TextField(null=True)),
                ('createDate', models.DateTimeField(auto_now=True)),
                ('lastUpdate', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(max_length=30)),
                ('desc', models.TextField(null=True)),
                ('createDate', models.DateTimeField(auto_now=True)),
                ('lastUpdate', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='RoleFeaturePermission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('isActive', models.BooleanField(default=False)),
                ('createDate', models.DateTimeField(auto_now=True)),
                ('lastUpdate', models.DateTimeField(auto_now_add=True)),
                ('feature', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='feature_rfp_list', to='user.Feature')),
                ('permission', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='permission_rfp_list', to='user.Permission')),
                ('role', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='role_rfp_list', to='user.Role')),
            ],
        ),
        migrations.CreateModel(
            name='UserExerInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('height', models.IntegerField(default=0)),
                ('weight', models.IntegerField(default=0)),
                ('createDate', models.DateTimeField(auto_now=True)),
                ('lastUpdate', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_uei_list', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserHousehold',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('isOwner', models.BooleanField(default=False)),
                ('createDate', models.DateTimeField(auto_now=True)),
                ('lastUpdate', models.DateTimeField(auto_now_add=True)),
                ('household', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='households', to='user.Household')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_list', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserRole',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('isActive', models.BooleanField(default=False)),
                ('createDate', models.DateTimeField(auto_now=True)),
                ('lastUpdate', models.DateTimeField(auto_now_add=True)),
                ('role', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='role_userrole_list', to='user.Role')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_userrole_list', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.IntegerField()),
                ('fileUrl', models.CharField(max_length=256, null=True)),
                ('createDate', models.DateTimeField(auto_now=True)),
                ('lastUpdate', models.DateTimeField(auto_now_add=True)),
                ('staff', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='staffs', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='users', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
