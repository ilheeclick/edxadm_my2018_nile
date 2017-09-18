from django.db import models
from django.utils import timezone


#
# # Create your models here.
#
class Notice(models.Model):
    noti_title = models.CharField(max_length=50)
    noti_content = models.TextField()
    noti_reg = models.DateTimeField(default=timezone.now)
    noti_del = models.CharField(max_length=10, default='o')

    def __unicode__(self):
        return self.noti_title


class GeneratedCertificate(models.Model):

    # user = models.ForeignKey(User)
    # course_id = CourseKeyField(max_length=255, blank=True, default=None)
    course_id = models.CharField(max_length=32, blank=True, default=None)
    verify_uuid = models.CharField(max_length=32, blank=True, default='', db_index=True)
    download_uuid = models.CharField(max_length=32, blank=True, default='')
    download_url = models.CharField(max_length=128, blank=True, default='')
    grade = models.CharField(max_length=5, blank=True, default='')
    key = models.CharField(max_length=32, blank=True, default='')
    distinction = models.BooleanField(default=False)
    status = models.CharField(max_length=32, default='unavailable')
    # mode = models.CharField(max_length=32, choices=MODES, default=MODES.honor)
    name = models.CharField(blank=True, max_length=255)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    error_reason = models.CharField(max_length=512, blank=True, default='')

    class Meta(object):
        unique_together = (('user', 'course_id'),)
        app_label = "certificates"

