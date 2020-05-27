# Generated by Django 2.1.7 on 2019-03-25 21:37

import constrainedfilefield.fields.file
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import main.models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0006_auto_20190316_1034'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='resource',
            name='description',
        ),
        migrations.RemoveField(
            model_name='resource',
            name='embed_link',
        ),
        migrations.RemoveField(
            model_name='resource',
            name='normal_link',
        ),
        migrations.AddField(
            model_name='resource',
            name='creator',
            field=models.ForeignKey(default=1, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='resource',
            name='title',
            field=models.TextField(default='', max_length=100),
        ),
        migrations.AddField(
            model_name='resource',
            name='upload',
            field=constrainedfilefield.fields.file.ConstrainedFileField(content_types=['video/mp4'], default='', js_checker=True, max_upload_size=5000000000, mime_lookup_length=4096, upload_to=main.models.user_directory_path),
        ),
        migrations.AddField(
            model_name='user',
            name='is_creator',
            field=models.BooleanField(default=False),
        ),
    ]
