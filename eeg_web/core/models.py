from django.contrib.auth.models import User
from django.db import models
from django.db.models import SET_NULL


class EEGCheck(models.Model):
    check_time = models.DateTimeField(auto_now_add=True)
    uploaded_file = models.FileField(upload_to='uploads/%Y/%m/%d/')
    user = models.ForeignKey(User, null=True, on_delete=SET_NULL)
    accuracy = models.FloatField(default=0)
    result = models.JSONField(null=True)
    error = models.CharField(max_length=500, blank=True, null=True)
    has_patterns = models.BooleanField(default=False)
    settings = models.ForeignKey('Settings', on_delete=SET_NULL, null=True)


class Settings(models.Model):
    accuracy = models.FloatField(default=0)
    s_h_min = models.SmallIntegerField()
    s_h_max = models.SmallIntegerField()
    s_w_min = models.SmallIntegerField()
    s_w_max = models.SmallIntegerField()

    w_h_min = models.SmallIntegerField()
    w_h_max = models.SmallIntegerField()
    w_w_min = models.SmallIntegerField()
    w_w_max = models.SmallIntegerField()

    def __str__(self):
        return f'id: {self.id}, accuracy: {self.accuracy}'
