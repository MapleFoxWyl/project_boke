import json

from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from message.models import Message
from tool.login_check import login_check
from topic.models import Topic


@login_check('POST')
def messages(req, topic_id):
  # 请求格式->{'content':'aaa','parent_id':1}->parent_id如果该字段存在,则证明当前是回复,否则为留言
  # 响应格式->{'code':200}
  # 注意-->post需要检查token
  if req.method == 'POST':
    # 发布留言及回复
    user = req.user
    json_str = req.body
    if not json_str:
      result = {'code': 402, 'error': '请给我json'}
      return JsonResponse(result)
    json_obj = json.loads(json_str)
    content = json_obj.get('content')
    parent_message = json_obj.get('parent_id', 0)
    if not content:
      result = {'code': 403, 'error': '请给我content'}
      return JsonResponse(result)
    # 获取topic
    topics = Topic.objects.filter(id=topic_id)
    if not topics:
      result = {'code': 404, 'error': 'The topic is not existed!'}
      return JsonResponse(result)
    topic = topics[0]
    # 创建message
    Message.objects.create(topic=topic, content=content,
                           parent_message=parent_message,
                           publisher=user)
    return JsonResponse({'code': 200})
