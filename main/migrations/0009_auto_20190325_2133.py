# Generated by Django 2.1.7 on 2019-03-26 04:33

import constrainedfilefield.fields.file
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import main.models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0008_auto_20190325_2126'),
    ]

    operations = [
        migrations.AlterField(
            model_name='concept',
            name='subject',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.Subject', verbose_name='subject'),
        ),
        migrations.AlterField(
            model_name='concept',
            name='topic',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.Topic', verbose_name='topic'),
        ),
        migrations.AlterField(
            model_name='resource',
            name='concept',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.Concept', verbose_name='concept'),
        ),
        migrations.AlterField(
            model_name='resource',
            name='creator',
            field=models.ForeignKey(default=1, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='creator'),
        ),
        migrations.AlterField(
            model_name='resource',
            name='subject',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.Subject', verbose_name='subject'),
        ),
        migrations.AlterField(
            model_name='resource',
            name='topic',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.Topic', verbose_name='topic'),
        ),
        migrations.AlterField(
            model_name='resource',
            name='upload',
            field=constrainedfilefield.fields.file.ConstrainedFileField(content_types=['video/mp4'], default='', js_checker=True, max_upload_size=5000000000, mime_lookup_length=4096, upload_to=main.models.user_directory_path, verbose_name='upload'),
        ),
        migrations.AlterField(
            model_name='topic',
            name='subject',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.Subject', verbose_name='subject'),
        ),
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(error_messages={'unique': 'A user with that email already exists.'}, max_length=254, unique=True, verbose_name='email address'),
        ),
        migrations.AlterField(
            model_name='user',
            name='is_creator',
            field=models.BooleanField(default=False, help_text='Designates whether this user can upload content.', verbose_name='creator'),
        ),
    ]
