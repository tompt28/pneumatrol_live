# Generated by Django 3.2.8 on 2021-11-29 09:40

import ORWAapp.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Customers',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(help_text='Customer Name', max_length=200)),
                ('account_name', models.CharField(help_text='Account ref', max_length=6, unique=True)),
                ('short_name', models.CharField(blank=True, max_length=50, null=True)),
            ],
            options={
                'verbose_name_plural': 'Customer',
            },
        ),
        migrations.CreateModel(
            name='PartType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20, unique=True)),
                ('description', models.TextField(help_text='200 character max', max_length=200)),
            ],
            options={
                'verbose_name_plural': 'Part Types',
            },
        ),
        migrations.CreateModel(
            name='SalesOrder',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_number', models.CharField(max_length=8, unique=True)),
                ('entered_date', models.DateField(blank=True, null=True)),
                ('order_date', models.DateField(help_text='date on the paperwork')),
                ('issue_date', models.DateField(blank=True, null=True)),
                ('ORWA_lines', models.IntegerField(help_text='number of lines that are an ORWA')),
                ('reject_date', models.DateField(blank=True, null=True)),
                ('reject_note', models.TextField(blank=True, max_length=200)),
                ('notes', models.TextField(blank=True)),
                ('paperwork', models.FileField(upload_to=ORWAapp.models.update_filename)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ORWAapp.customers')),
                ('reject_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='rejected_by', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'SalesOrders',
            },
        ),
        migrations.CreateModel(
            name='Parts',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('part_code', models.CharField(max_length=22, unique=True)),
                ('updated_code', models.BooleanField(default=False)),
                ('start_date', models.DateField()),
                ('completed_date', models.DateField(auto_now_add=True)),
                ('approved_date', models.DateField(blank=True, null=True)),
                ('problem_parts', models.BooleanField(default=False)),
                ('problem_parts_cleared', models.BooleanField(default=False)),
                ('notes', models.TextField(blank=True)),
                ('size', models.CharField(choices=[('S', 'Small'), ('M', 'Medium'), ('L', 'Large'), ('H', 'Huge')], max_length=1)),
                ('approved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='approvedby', to=settings.AUTH_USER_MODEL)),
                ('completed_by', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='completedby', to=settings.AUTH_USER_MODEL)),
                ('part_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ORWAapp.parttype')),
                ('sales_order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='salesorder', to='ORWAapp.salesorder')),
            ],
            options={
                'verbose_name_plural': 'Parts',
            },
        ),
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Role', models.CharField(choices=[('ENG', 'Engineering'), ('SAL', 'Sales'), ('ENM', 'Enginering Manager'), ('SAM', 'Sales Manager')], max_length=3)),
                ('Profile_pic', models.ImageField(blank=True, upload_to='profile_pics/')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
