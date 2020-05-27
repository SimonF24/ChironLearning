from constrainedfilefield.fields import ConstrainedFileField
from datetime import datetime
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _
import os
import time

from djangoratings.fields import RatingField

class Dashboard_Message(models.Model):
    '''
    A message that is shown on the dashboard page.
    Only one of these objects should exist at a time.
    '''
    
    message = models.TextField(_('message'))
    created = models.DateTimeField(_('created'), auto_now_add=True)

    def __str__(self):
        return self.message

class Subject(models.Model):
    '''
    A broad class of study such as science of math
    '''

    name = models.CharField(_('name'), default='', max_length=200)
    description = models.TextField(_('description'), default='')

    def __str__(self):
        return self.name

class Topic(models.Model):
    '''
    A subdivision of a subject such as physics or algebra
    '''

    name = models.CharField(_('name'), default='', max_length=200)
    description = models.TextField(_('description'), default='')
    subject = models.ForeignKey(Subject, verbose_name=_('subject'), on_delete=models.CASCADE)
    order_in_subject = models.IntegerField(_('order in subject'), null=True) #Must be unique within each subject

    def __str__(self):
        return self.name

class Concept(models.Model):
    '''
    A specific idea that a user will be trying to learn.
    A subdivision of a topic such as Newton's Laws or Polynomial Long Division
    '''
     
    name = models.CharField(_('name'), default='', max_length=200)
    description = models.TextField(_('description'), default='')
    subject = models.ForeignKey(Subject, verbose_name=_('subject'), on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, verbose_name=_('topic'), on_delete=models.CASCADE)
    order_in_topic = models.IntegerField(_('order in topic'), null=True) # Must be unique within each topic

    def __str__(self):
        return self.name

class UserManager(BaseUserManager):
    """
    A slight modification of the default user manager to make email required.
    Accomdates our using email instead of username to login.
    Original manager found in django/contrib/auth/models on line 131
    """

    use_in_migrations = True

    def _create_user(self, username, email, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        if not email:
            raise ValueError('The given email must be set')
        if not username:
            raise ValueError('The given username must be set')
        email = self.normalize_email(email)
        username = self.model.normalize_username(username)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_creator', False)
        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(username, email, password, **extra_fields)

class User(AbstractUser):
    """
    Custom user model to use email as the username field for authentication purposes.
    Original user model can be found in django/contrib/auth/models in line 288.
    """

    email = models.EmailField(_('email address'), unique=True, error_messages={'unique':_("A user with that email already exists.")})
    is_creator = models.BooleanField(_('creator'), default=False, help_text=_('Designates whether this user can upload content.'))
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = UserManager()

def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<title>
    return 'user_{0}/{1}.mp4'.format(instance.creator.id, instance.title)

class Resource(models.Model):
    '''
    Video resources uploaded by a specific user and associated with a specific concept
    '''

    # embed_link = models.CharField(default='', max_length=500)
    # normal_link = models.CharField(default='', max_length=500)
    # description = models.TextField(default='', unique=True)
    creator = models.ForeignKey(User, verbose_name=_('creator'), default=1, on_delete=models.CASCADE, null=True)
    concept = models.ForeignKey(Concept, verbose_name=_('concept'), on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, verbose_name=_('subject'), on_delete=models.CASCADE)
    rating = RatingField(range=5, verbose_name=_('rating'), can_change_vote=True)
    tags = models.CharField(_('tags'), default='', max_length=500)
    topic = models.ForeignKey(Topic, verbose_name=_('topic'), on_delete=models.CASCADE)
    title = models.CharField(_('title'), default=datetime.now, max_length=100)
    upload = ConstrainedFileField(upload_to=user_directory_path, 
                                  verbose_name=_('upload'),
                                  default='',
                                  content_types=['video/mp4'],
                                  max_upload_size=5*10**9) # ~5GB
    upload_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
        # return self.description

    class Meta:
        unique_together =  ('creator', 'title')

class TemporaryFileStorage(models.Model):
    '''
    A temporary storage space for files uploaded using AJAX.
    Field names mirror those of Resource for convenience
    ''' 

    title = models.CharField(max_length=100, default='temp')
    creator = models.ForeignKey(User, verbose_name=_('creator'), on_delete=models.CASCADE)
    upload = ConstrainedFileField(upload_to=user_directory_path, 
                                              verbose_name=_('temp upload'),
                                              default='',
                                              content_types=['video/mp4'],
                                              max_upload_size=5*10**9) # ~5GB
    
    def __str__(self):
        return "Temporary file storage for user {}".format(self.creator.id)

# Handles delete of files when objects are deleted
@receiver(models.signals.post_delete, sender=Resource)
@receiver(models.signals.post_delete, sender=TemporaryFileStorage)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes upload from filesystem
    when corresponding object is deleted.
    """
    if instance.upload:
        if os.path.isfile(instance.upload.path):
            os.remove(instance.upload.path)

# Handles delete of upload when an object is changed
@receiver(models.signals.pre_save, sender=Resource)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """
    Deletes old upload from filesystem
    when corresponding object is updated
    with new file.
    """
    if not instance.pk:
        return False

    try:
        old_file = instance.__class__.objects.get(pk=instance.pk).upload
    except instance.DoesNotExist:
        return False

    new_file = instance.upload
    if not old_file == new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)

from .data import train_new_model #Has to be after Resource definition

# Trains a new model after a new resource is added 
@receiver(models.signals.post_save, sender=Resource)
def update_sagemaker_model(sender, instance, **kwargs):
    if os.environ['Training_Model']: # A model is already training
        if not os.environ['Training_queued']: 
            # If training is not already queued, queue it to begin training after the current training finishes
            os.environ['Training_queued'] = True
            while os.environ['Training_Model'] == True: # Checks every minute if training is finished yet
                time.sleep(60)
            train_new_model()
            os.environ['Highest_safe_pk'] = instance.pk
            os.environ['Training_queued'] = False
    else: # A model is not already training, so begin training a new one
        train_new_model()