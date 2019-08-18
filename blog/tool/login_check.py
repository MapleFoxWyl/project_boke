import jwt
from django.http import JsonResponse

from user.models import UserProfile

TOKEN_KEY = '1234567abcdef'


def login_check(*methods):
  def _login_check(func):
    def wrapper(request, *args, **kwargs):
      # 获取token
      token = request.META.get('HTTP_AUTHORIZATION')
      if not methods:
        # 如果当前没传任何参数,则直接返回视图函数
        return func(request, *args, **kwargs)
      else:
        # 检查当前request.method 是否在参数列表中
        if request.method not in methods:
          return func(request, *args, **kwargs)
        # 当前没有token
      if not token:
        request = {'code': 109, 'error': 'Please give me token!!'}
        return JsonResponse(request)
      print(11111111111)
      print(token)
      print(22222222222)
      try:
        res = jwt.decode(token, TOKEN_KEY)
      except Exception as e:
        print('login check is error %s' % (e))
        request = {'code': 108, 'error': 'The token is wrong!!!'}
        return JsonResponse(request)
      # token校验成功
      username = res['username']
      try:
        user = UserProfile.objects.get(username=username)
      except:
        user = None
      if not user:
        request = {'code': 110, 'error': 'The user is not existed!'}
        return JsonResponse(request)
      # 将uesr 赋值给 request对象
      request.user = user

      return func(request, *args, **kwargs)

    return wrapper

  return _login_check


def get_user_by_request(request):
  """
  通过request 获取user
  :param request:
  :return:
  """
  token = request.META.get('HTTP_AUTHORIZATION')
  if not token:
    return None
  # 尝试性解析token
  try:
    res = jwt.decode(token, TOKEN_KEY)
  except:
    return None
  username = res['username']
  try:
    user = UserProfile.objects.get(username=username)
  except:
    return None
  if not user:
    return None
  return user
