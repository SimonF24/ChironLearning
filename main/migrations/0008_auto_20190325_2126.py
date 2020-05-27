# Generated by Django 2.1.7 on 2019-03-26 04:26

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0007_auto_20190325_1437'),
    ]

    operations = [
        migrations.AlterField(
            model_name='concept',
            name='description',
            field=models.TextField(default='', verbose_name='description'),
        ),
        migrations.AlterField(
            model_name='concept',
            name='name',
            field=models.CharField(default='', max_length=200, verbose_name='name'),
        ),
        migrations.AlterField(
            model_name='concept',
            name='order_in_topic',
            field=models.IntegerField(null=True, verbose_name='order in topic'),
        ),
        migrations.AlterField(
            model_name='dashboard_message',
            name='created',
            field=models.DateTimeField(auto_now_add=True, verbose_name='created'),
        ),
        migrations.AlterField(
            model_name='dashboard_message',
            name='message',
            field=models.TextField(verbose_name='message'),
        ),
        migrations.AlterField(
            model_name='resource',
            name='tags',
            field=models.CharField(default='', max_length=500, verbose_name='tags'),
        ),
        migrations.AlterField(
            model_name='resource',
            name='title',
            field=models.CharField(default='', max_length=100, verbose_name='title'),
        ),
        migrations.AlterField(
            model_name='subject',
            name='description',
            field=models.TextField(default='', verbose_name='description'),
        ),
        migrations.AlterField(
            model_name='subject',
            name='name',
            field=models.CharField(default='', max_length=200, verbose_name='name'),
        ),
        migrations.AlterField(
            model_name='topic',
            name='description',
            field=models.TextField(default='', verbose_name='description'),
        ),
        migrations.AlterField(
            model_name='topic',
            name='name',
            field=models.CharField(default='', max_length=200, verbose_name='name'),
        ),
        migrations.AlterField(
            model_name='topic',
            name='order_in_subject',
            field=models.IntegerField(null=True, verbose_name='order in subject'),
        ),
        migrations.AlterField(
            model_name='user',
            name='date_joined',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined'),
        ),
        migrations.AlterField(
            model_name='user',
            name='is_creator',
            field=models.BooleanField(default=False, help_text='Designates whether this user can upload content.', verbose_name='is_creator'),
        ),
    ]
