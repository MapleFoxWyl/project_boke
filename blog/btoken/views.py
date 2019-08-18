import hashlib
import json
import time

import jwt
from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from user.models import UserProfile


from .models import *


def tokens(request):
  '''
  创建token-->登录
  :param request:
  :return:
  '''
  if not request.method == 'POST':
    result = {'code': 102, 'error': 'Please use POST!'}
    return JsonResponse(result)
  # 获取数据(字节串)
  json_str = request.body
  if not json_str:
    result = {'code': 103, 'error': 'Please give mi json'}
    return JsonResponse(result)
  json_obj = json.loads(json_str)
  username = json_obj.get('username')
  password = json_obj.get('password')
  if not username:
    result = {'code': 104, 'error': 'please give me username!'}
    return JsonResponse(result)
  if not password:
    result = {'code': 105, 'error': 'please give me passwored!'}
    return JsonResponse(result)
  users = UserProfile.objects.filter(username=username)
  # 看账号是否存在
  if not users:
    result = {'code': 106, 'error': 'The username or passowrd is wrong!!'}
    print('账号不对')
    return JsonResponse(result)
  # 做密码
  p_m = hashlib.sha256()
  # 密码解析
  p_m.update(password.encode())

  # 判断密码
  if users[0].password != p_m.hexdigest():
    result = {'code': 107, 'error': 'The username or password is wrong !!'}
    print('密码不对')
    return JsonResponse(result)

  #生成token
  token = make_token(username)
  result = {'code':200,'username':username,'data':{'token':token.decode()}}
  return JsonResponse(result)


def make_token(username, expire=3600 * 24):
  """
  生成token
  :param username:
  :param expire:
  :return:
  """
  key = '1234567abcdef'
  now_t = time.time()
  data = {'username': username, 'exp': int(now_t + expire)}
  return jwt.encode(data, key, algorithm='HS256')



