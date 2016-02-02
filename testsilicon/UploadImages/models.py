from __future__ import unicode_literals

from django.db import models
from django.conf import settings
import os

def upload_file_path(instance, filename):
    return settings.STATIC_ROOT + filename

class User(models.Model):
	user_name = models.CharField(max_length=100)
	password = models.CharField(max_length=32)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

class User_Image(models.Model):	
	user = models.ForeignKey(User)
	image_path = models.CharField(max_length=1024)
	files = models.FileField(upload_to=upload_file_path, blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

class Image_Comment(models.Model):
	user = models.ForeignKey(User)	
	image = models.ForeignKey(User_Image,related_name='commentImage')
	comment = models.CharField(max_length=1024)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

class Notification(models.Model):
	user = models.ForeignKey(User)
	user_commend = models.ForeignKey(Image_Comment)
	image = models.ForeignKey(User_Image)
	is_view = models.IntegerField()
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
