from django.db import models
import base64

LANGUAGE_CHOICES = (
        ('text', 'TEXT'),
        ('c', 'C'),
        ('cpp', 'C++'),
        ('py', 'PYTHON'),
        ('json', 'JSON'),
 )

EXPIRY_CHOICES = (
        (1, '1 Day'),
        (7, '1 Week'),
        (30, '1 Month'),
        (365, '1 Year')
)

# Create your models here.

class DjangoPastebin(models.Model):
    identification = models.IntegerField()
    link = models.CharField(max_length=256)
    content = models.TextField()
    title = models.CharField(max_length=256)
    user = models.CharField(max_length=256)
    language = models.CharField(max_length=5, choices=LANGUAGE_CHOICES, default='text')
    image = models.FileField(max_length=256,upload_to="templates/upload_pictures",null=True, blank=True,
                                  default="templates/upload_pictures/noimage.png")
    video = models.FileField(max_length=256, upload_to="templates/upload_videos", null=True, blank=True,
                             default="templates/upload_pictures/no-video.jpg")
    created = models.DateTimeField(auto_now=True)
    expiry = models.IntegerField(choices= EXPIRY_CHOICES, default=1)

    def __str__(self):
        return self.user
