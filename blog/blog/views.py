from django.http import HttpResponse
from user.models import UserProfile
import redis
def test(req):
  #连接redis
  pool = redis.ConnectionPool(host='127.0.0.1',port=6379,db=0)
  r=redis.Redis(connection_pool=pool)
  #加分布式锁
  while True:
    try:
      with r.lock('1234',blocking_timeout=3) as lock:
        #对score字段进行+1操作
        u = UserProfile.objects.get(username='1234')
        u.score+=1
        u.save()
      break
    except Exception as e:
      print('lock failed')




  return  HttpResponse('HI,HI,HI')

