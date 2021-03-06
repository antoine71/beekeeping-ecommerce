# Generated by Django 4.0.5 on 2022-06-28 08:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0002_alter_order_contact_info'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='delivery_option',
            field=models.CharField(choices=[('H', 'Livraison à Domicile'), ('P', 'Livraison en Point Relais')], default='H', max_length=1, verbose_name='Options de livraison'),
            preserve_default=False,
        ),
    ]
