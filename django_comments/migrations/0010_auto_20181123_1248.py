# Generated by Django 2.1.1 on 2018-11-23 20:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_comments', '0009_auto_20180902_1057'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='submit_date',
            field=models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='date/time submitted'),
        ),
    ]
