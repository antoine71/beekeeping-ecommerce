# Generated by Django 4.0.5 on 2022-07-04 07:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0004_alter_order_delivery_option_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='MondialRelayInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mr_ID', models.CharField(max_length=10)),
                ('mr_Nom', models.CharField(max_length=50)),
                ('mr_Adresse1', models.CharField(max_length=50)),
                ('mr_Adresse2', models.CharField(blank=True, max_length=50, null=True)),
                ('mr_CP', models.CharField(max_length=10)),
                ('mr_Ville', models.CharField(max_length=50)),
                ('mr_Pays', models.CharField(max_length=2)),
            ],
        ),
        migrations.AlterField(
            model_name='order',
            name='delivery_option',
            field=models.CharField(choices=[('H', 'Livraison à Domicile'), ('R', 'Livraison en Point Mondial Relay')], max_length=1, verbose_name='Options de livraison'),
        ),
        migrations.AddField(
            model_name='order',
            name='mondial_relay_info',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='mondial_relay_info', to='shop.mondialrelayinfo', verbose_name='Adresse du point relais'),
        ),
    ]
