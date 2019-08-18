import html
import json

from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from message.models import Message
from tool.login_check import login_check, get_user_by_request
from topic.models import Topic
from user.models import UserProfile


@login_check('POST')
def topics(requset, author_id):
  # 127.0.0.1:5000/<username>/topic/release
  if requset.method == 'POST':
    # 发布请求
    json_str = requset.body
    if not json_str:
      res = {'code': 302, 'error': '请给我data'}
      return JsonResponse(res)
    json_obj = json.loads(json_str)
    title = json_obj.get('title')
    # 带html标签样式的文章内容[颜色]
    content = json_obj.get('content')
    # 纯文本的文章内容用于截取简介
    content_text = json_obj.get('content_text')
    limit = json_obj.get('limit')
    category = json_obj.get('category')
    if not title:
      res = {'code': 303, 'error': '请给我标题'}
      return JsonResponse(res)
    # 防止xss cross site script 攻击
    title = html.escape(title)

    if not content:
      res = {'code': 304, 'error': '请给我文章内容'}
      return JsonResponse(res)
    if not content_text:
      res = {'code': 305, 'error': '请给我文章纯文本'}
      return JsonResponse(res)
    if not limit:
      res = {'code': 306, 'error': '请给我权限'}
      return JsonResponse(res)
    if not category:
      res = {'code': 307, 'error': '请给我类别'}
      return JsonResponse(res)
    introduce = content_text[:30]
    if requset.user.username != author_id:
      res = {'code': 308, 'error': '不要搞我'}
      return JsonResponse(res)
    # 创建数据
    try:
      Topic.objects.create(title=title,
                           limit=limit,
                           content=content,
                           introduce=introduce,
                           category=category,
                           author_id=author_id)
    except:
      res = {'code': 309, 'error': 'Topic is busy'}
      return JsonResponse(res)
    res = {'code': 200, 'username': requset.user.username}
    return JsonResponse(res)

  elif requset.method == 'GET':
    # 获取atthor_id的文章
    # 后端地址/v1/topcis/<username>?category=[tec|no-tec]
    # 前端地址http://127.0.0.1:5000/<username>/topics
    # 1.访问者visitor
    # 2.博主/作者 author
    authors = UserProfile.objects.filter(username=author_id)
    if not authors:
      res = {'code': 310, 'error': '当前作者不存在'}
      return JsonResponse(res)
    author = authors[0]

    # 查找我们的访问者
    visitor = get_user_by_request(requset)
    visitor_username = None
    if visitor:
      visitor_username = visitor.username
    # 获取他t_id
    t_id = requset.GET.get('t_id')

    if t_id:
      # 查询指定文章数据
      t_id = int(t_id)
      # 是否为博主访问自己的博客
      is_self = False
      if visitor_username == author_id:
        is_self = True
        # 博主访问自己的博客
      try:
        author_topic = Topic.objects.get(id=t_id)
      except Exception as e:
        res = {'code': 311, 'error': 'no topic'}
        return JsonResponse(res)
      else:
        # 陌生人访问博主的博客
        try:
          author_topic = Topic.objects.get(id=t_id,
                                           limit='public')
        except Exception as e:
          res = {'code': 312, 'error': 'no topic!'}
          return JsonResponse(res)
      res = make_topic_res(author, author_topic, is_self)
      # http://127.0.0.1:5000/<username>/topics
      return JsonResponse(res)
    else:
      # 查询用户的全部文章

      # 判断是否为有查询字符串[category]
      category = requset.GET.get('category')
      if category in ['tec', 'no-tec']:

        if visitor_username == author.username:
          # 博主访问自己的博客
          author_topics = Topic.objects.filter(author_id=author.username,
                                               category=category)
        else:
          # 陌生的访问者 访问author的博客
          author_topics = Topic.objects.filter(author_id=author.username,
                                               limit='public',
                                               category=category)

      else:
        if visitor_username == author.username:
          # 博主访问自己的博客
          author_topics = Topic.objects.filter(author_id=author.username)
        else:
          # 陌生的访问者 访问author的博客
          author_topics = Topic.objects.filter(author_id=author.username,
                                               limit='public')
      # 生成返回值
      res = make_topics_res(author, author_topics)
      return JsonResponse(res)

  elif requset.method == 'DELETE':
    # 删除博客[真删除]
    # 查询字符串中包含topic_id-->
    pass


def make_topics_res(author, author_topics):
  """
  返回一个用户
  :param author:
  :param author_topics:
  :return:
  """
  res = {'code': 200, 'data': {}}
  topics_res = []
  for topic in author_topics:
    d = {}
    d['id'] = topic.id
    d['title'] = topic.title
    d['category'] = topic.category
    d['created_time'] = topic.created_time.strftime('%Y-%m-%d %H:%M:%S')
    d['introduce'] = topic.introduce
    d['author'] = author.nickname
    topics_res.append(d)
  res['data']['topics'] = topics_res
  res['data']['nickname'] = author.nickname
  return res

  # return JsonResponse({'code': 200})


def make_topic_res(author, author_topic, is_self):
  """
  生成topic 详情数据
  :param author:
  :param author_topic:
  :param is_self:
  :return:
  """
  if is_self:
    # 博主访问自己博客
    # 1,2,3,4,5,6,8,26
    # 去除ID大于当前博客ID的数据的第一个  当前文章的下一篇
    next_topic = Topic.objects.filter(
      id__gt=author_topic.id, author=author).first()
    # 取出ID小于当前博客I的数据的最后一个    当前文章的上一篇
    last_topic = Topic.objects.filter(
      id__lt=author_topic.id, author=author).last()
  else:
    # 访客(陌生人)访问当前博客
    next_topic = Topic.objects.filter(
      id__gt=author_topic.id, author=author, limit='public').first()
    last_topic = Topic.objects.filter(
      id__lt=author_topic.id, author=author, limit='public').last()

  if next_topic:
    next_id = next_topic.id
    next_title = next_topic.title
  else:
    next_id = None
    next_title = None
  # 生成上一个文章的id和title
  if last_topic:
    last_id = last_topic.id
    last_title = last_topic.id
  else:
    last_id = None
    last_title = None

  res = {'code': 200, 'data': {}}
  res['data']['nickname'] = author.nickname
  res['data']['title'] = author_topic.title
  res['data']['category'] = author_topic.category
  res['data']['created_time'] = author_topic.created_time.strftime('%Y-%m-%d %H:%M:%S')
  res['data']['content'] = author_topic.content
  res['data']['introduce'] = author_topic.introduce
  res['data']['author'] = author.nickname
  res['data']['next_id'] = next_id
  res['data']['next_title'] = next_title
  res['data']['last_id'] = last_id
  res['data']['last_title'] = last_title
  # 留言&回复数据
  # 获取所有messages
  all_messages = Message.objects.filter(
    topic=author_topic).order_by('-create_time')
  # 以下是python语法问题!!!!!!!
  # {1:[{'回复'},{'回复'}]}
  # [{'留言'},{'留言'},{},{},]
  msg_dict = {1: [{}]}
  msg_list = []
  m_count = 0
  # [{'p_m':1,'cont
  # ent':'aaa','id':2},
  #  {'p_m':1,'content':'bbb','id'=3},
  # {'id':1,'content':'留言'}]

  for msg in all_messages:
    m_count += 1
    if msg.parent_message:
      # 回复
      if msg.parent_message in msg_dict:
        msg_dict[msg.parent_message].append(
          {'msg_id': msg.id,
           'publisher': msg.publisher.nickname,
           'publisher_avatar': str(msg.publisher.avatar),
           'content': msg.content,
           'create_time': msg.create_time.strftime('%Y-%m-%d %H:%M:%S')})
      else:
        msg_dict[msg.parent_message] = []
        msg_dict[msg.parent_message].append({'msg_id': msg.id,
                                             'publisher': msg.publisher.nickname,
                                             'publisher_avatar': str(msg.publisher.avatar),
                                             'content': msg.content,
                                             'create_time': msg.create_time.strftime(
                                               '%Y-%m-%d %H:%M:%S')})
    else:
      # 留言
      msg_list.append({'id': msg.id, 'content': msg.content,
                       'publisher': msg.publisher.nickname,
                       'publisher_avatar': str(msg.publisher.avatar),
                       'create_time': msg.create_time.strftime('%Y-%m-%d %H:%M:%S'),
                       'reply': []})
      # 关联 留言和对应的回复
      # msg_list->[{留言相关的信息,'reply':[]},]
      for m in msg_list:
        if m['id'] in msg_dict:
          # 证明当前的留言有回复信息
          m['reply'] = msg_dict[m['id']]

  res['data']['messages'] = msg_list
  res['data']['messages_count'] = m_count
  print('1111111111111111111')
  print(res['data']['messages'])
  print('2222222222222')
  return res
