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

