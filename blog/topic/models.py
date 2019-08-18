from django.db import models

# Create your models here.
from user.models import UserProfile


class Topic(models.Model):
  title = models.CharField(verbose_name='文章主题',
                           max_length=50)
  #'tec'-技术类  'no-tec'-非技术类
  category = models.CharField(verbose_name='文章分类',
                              max_length=20)
  #'public'公开的 private 私有的
  limit = models.CharField(verbose_name='文章权限',
                           max_length=10)
  introduce = models.CharField(verbose_name='文章简介',
                               max_length=90)
  content = models.TextField(verbose_name='文章内容')
  created_time = models.DateTimeField(verbose_name='文章创建时间',
                                      auto_now_add=True)
  modified_time = models.DateTimeField(verbose_name='文章修改时间',
                                       auto_now=True)
  #外键
  author = models.ForeignKey(UserProfile)

  class Meta:
    db_table = 'topic'
