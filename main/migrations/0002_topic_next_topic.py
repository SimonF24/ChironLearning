# Generated by Django 2.1.1 on 2019-02-02 05:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_squashed_0002_auto_20181229_2108'),
    ]

    operations = [
        migrations.AddField(
            model_name='topic',
            name='next_topic',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='main.Topic'),
        ),
    ]
