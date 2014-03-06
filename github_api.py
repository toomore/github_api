# -*- coding:utf8 -*-
import requests
import setting
import ujson as json
from pprint import pprint

# https://github.com/login/oauth/authorize?client_id=
# code d38e574154d18dff15cb

data = {
        'client_id': setting.CLIENT_ID,
        'client_secret': setting.CLIENT_SECRET,
        'code': '28be5f38369ed7f2318d'}

#r = requests.post('https://github.com/login/oauth/access_token', data=data)
#print r.content
# access_token=&scope=&token_type=bearer

params = {
        'access_token': setting.USER_ACCESS_TOKEN,
        }
r = requests.get('https://api.github.com/user', params=params)
pprint(r.json())

r = requests.get('https://api.github.com/repos/toomore/grs/languages', params=params)
pprint(r.json())
