# Generated by Django 4.0.5 on 2022-06-29 09:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contact', '0003_alter_demorequest_phone'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='demorequest',
            name='first_name',
        ),
        migrations.RemoveField(
            model_name='demorequest',
            name='last_name',
        ),
        migrations.RemoveField(
            model_name='demorequest',
            name='phone',
        ),
        migrations.RemoveField(
            model_name='demorequest',
            name='requested_date',
        ),
    ]
