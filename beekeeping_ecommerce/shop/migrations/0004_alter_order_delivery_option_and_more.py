# Generated by Django 4.0.5 on 2022-06-29 09:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0003_order_delivery_option'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='delivery_option',
            field=models.CharField(choices=[('H', 'Livraison à Domicile')], max_length=1, verbose_name='Options de livraison'),
        ),
        migrations.AlterField(
            model_name='order',
            name='payment_option',
            field=models.CharField(choices=[('S', 'Carte Bancaire')], max_length=1, verbose_name='Options de payment'),
        ),
        migrations.AlterField(
            model_name='order',
            name='ref_code',
            field=models.CharField(default='0', max_length=20),
        ),
    ]
