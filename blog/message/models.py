from django.db import models

# Create your models here.
from user.models import UserProfile
from topic.models import Topic

class Message(models.Model):
  content = models.CharField('内容', max_length=90)
  create_time = models.DateTimeField(auto_now_add=True)
  topic = models.ForeignKey(Topic)
  publisher = models.ForeignKey(UserProfile)
  parent_message = models.IntegerField(default=0)

  class Meta:
    db_table = 'message'
