import hashlib
import json
import time

import jwt
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

from btoken.views import make_token
from tool.login_check import login_check
from .models import *


# Create your views here.


@login_check('PUT')
def users(req, username=None):
  if req.method == 'POST':
    # 注册
    json_str = req.body
    if not json_str:
      result = {'code': 202, 'error': 'Please POST data!!'}

      return JsonResponse(result)
    # 如果当前报错,请执行json_str.decode()
    json_obj = json.loads(json_str)
    username = json_obj.get('username')
    email = json_obj.get('email')
    password_1 = json_obj.get('password_1')
    password_2 = json_obj.get('password_2')

    if not username:
      result = {'code': 203, 'error': 'Please give me username!'}
      return JsonResponse(result)

    if not email:
      result = {'code': 204, 'error': 'Please give me email!'}
      return JsonResponse(result)

    if not password_1 or not password_2:
      result = {'code': 205, 'error': 'Please give me password!'}
      return JsonResponse(result)

    if password_1 != password_2:
      result = {'code': 206, 'error': 'Please give me right password!'}
      return JsonResponse(result)

    # 检查用户名是否存在
    old_user = UserProfile.objects.filter(username=username)
    if old_user:
      result = {'code': 207, 'error': 'The username is userd !!!'}
      return JsonResponse(result)

    # 密码散列
    p_m = hashlib.sha256()
    p_m.update(password_1.encode())

    try:
      UserProfile.objects.create(username=username,
                                 nickname=username,
                                 email=email,
                                 password=p_m.hexdigest())
    except Exception as e:
      print('----create error is %s' % (e))
      result = {'code': 500, 'error': 'Sorry,server is busy !'}
      return JsonResponse(result)

    token = make_token(username)
    # token 编码问题? bytes串不能json dumps, 所以要执行decode方法
    # http://127.0.0.1:5000/register
    result = {'code': 200, 'username': username, 'data': {'token': token.decode()}}

    return JsonResponse(result)

  elif req.method == 'GET':

    # s = json.dumps({'code':200})
    # return HttpResponse(s)
    # 获取数据
    if username:
      # 获取指定用户数据[]
      users = UserProfile.objects.filter(username=username)
      if not users:
        result = {'code': 208, 'error': 'The user is not existed.'}
        return JsonResponse(result)
      user = users[0]
      if req.GET.keys():
        # 当前请求有查询字符串
        data = {}
        for key in req.GET.keys():
          if key == 'password':
            # 如果查询密码,则continue!
            continue
          # hasattr 第一个参数为对象,第二个参数为属性字符串,若对象含有第二个参数的属性,则返回True,反之False
          # getattr 参数用hasattr ,若对象含有第二个参数的属性,则反水对应属性的值,贩子抛出异常AttrbuteError
          if hasattr(user, key):
            if key == 'avatar':
              # avatar 属性需要调用str方法__str__
              data[key] = str(getattr(user, key))
            else:
              data[key] = getattr(user, key)
        result = {'code': 200, 'username': username, 'data': data}
        return JsonResponse(result)
      else:
        # 无查询字符串,即获取指定用户所有数据
        result = {'code': 200, 'username': username,
                  'data': {'info': user.info, 'sign': user.sign,
                           'nickname': user.nickname, 'avatar': str(user.avatar)}}
        return JsonResponse(result)
    else:
      # 没有username
      # [{username nickname sign info email avatar}]
      all_users = UserProfile.objects.all()
      result = []
      for _user in all_users:
        d = {}
        d['username'] = _user.username
        d['nickname'] = _user.nickname
        d['sign'] = _user.sign
        d['info'] = _user.info
        d['email'] = _user.email
        d['avatar'] = str(_user.avatar)
        result.append(d)
      return JsonResponse({'code': 200, 'data': result})

    # return JsonResponse({'code': 200})

  elif req.method == 'PUT':
    # 前段访问地址 http://127.0.0.1:5000/<username>/change_info
    # 后端地址 http://127.0.0.1:8000/v1/users/<username>
    # 更新用户数据
    user = req.user  # 装饰器调用
    # user = check_token(req)
    # if not user:
    #   result = {'code': 209, 'error': 'The PUT need token!'}
    #   return JsonResponse(result)
    json_str = req.body
    json_obj = json.loads(json_str)
    nickname = json_obj.get('nickname')
    if not nickname:
      result = {'code': 210, 'error': 'The nickname can not be none!'}
      return JsonResponse(result)
    sign = json_obj.get('sign')
    if sign is None:
      result = {'code': 211, 'error': 'The sign not in json!'}
      return JsonResponse(result)
    info = json_obj.get('info')
    if info is None:
      result = {'code': 212, 'errror': 'The info not in json!'}
      return JsonResponse(result)

    if user.username != username:
      result = {'code': 213, 'error': 'This is wrong!!!'}
      return JsonResponse(result)
    user.sign = sign
    user.info = info
    user.nickname = nickname
    user.save()
    result = {'code': 200, 'username': username}
    return JsonResponse(result)


@login_check('POST')
def user_avatar(req, username):
  # 当前只开放post请求
  if req.method != 'POST':
    res = {'code': 214, 'error': '请使用POST'}
    return JsonResponse(res)
  user = req.user
  if user.username != username:
    # 异常请求
    res = {'code': 215, 'error': '你错了!!!'}
    return JsonResponse(res)
  # 获取上传图片,上传方式是表单提交
  avatar = req.FILES.get('avatar')
  if not avatar:
    res = {'code': 216, 'error': '请给我avatar !!'}
    return JsonResponse(res)
  # 更新
  user.avatar = avatar
  user.save()
  res = {'code': 200, 'username': username}
  return JsonResponse(res)


def check_token(request):
  token = request.META.get('HTTP_AUTHORIZATION')
  if not token:
    return None
  try:
    res = jwt.decode(token, '1234567abcdef')
  except Exception as e:
    print('check_token error is %s' % (e))
    return None
  username = res['username']
  users = UserProfile.objects.filter(username=username)
  return users[0]
