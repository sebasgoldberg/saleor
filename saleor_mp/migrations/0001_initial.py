# Generated by Django 2.2.6 on 2020-04-14 02:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('order', '0076_auto_20191018_0554'),
    ]

    operations = [
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mp_id', models.CharField(blank=True, max_length=60, null=True, unique=True)),
                ('mp_status', models.CharField(blank=True, max_length=60, null=True)),
                ('mp_status_detail', models.CharField(blank=True, max_length=60, null=True)),
                ('mp_transaction_amount', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('order', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='mppayments', to='order.Order')),
            ],
        ),
    ]
