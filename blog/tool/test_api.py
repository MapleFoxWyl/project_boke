"""
模拟30个请求 向8000和9000发请求 都对score 进行加1操作
"""
import random
import requests
from threading import Thread


# 线程事件函数:向8000或者9000随机发请求
def get_request():
  url1 = 'http://127.0.0.1:8000/test'
  url2 = 'http://127.0.0.1:8100/test'
  url = random.choice([url1, url2])
  # 真正发请求
  requests.get(url)



t_list = []
for i in range(30):
  t = Thread(target=get_request)
  t_list.append(t)
  t.start()

for j in t_list:
  j.join()
