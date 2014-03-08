# -*- coding:utf8 -*-
import requests
import setting
import ujson as json
from pprint import pprint

class GithubAPI(object):
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret

    def authorize_url(self, *scope):
        url = 'https://github.com/login/oauth/authorize?client_id=%s' % \
            self.client_id

        if scope:
            url = url + '&scope=' + ','.join(scope)

        return url


if __name__ == '__main__':
    ## https://github.com/login/oauth/authorize?client_id=
    ## code d38e574154d18dff15cb

    #data = {
    #        'client_id': setting.CLIENT_ID,
    #        'client_secret': setting.CLIENT_SECRET,
    #        'code': '28be5f38369ed7f2318d'}

    ##r = requests.post('https://github.com/login/oauth/access_token', data=data)
    ##print r.content
    ## access_token=&scope=&token_type=bearer

    #params = {
    #        'access_token': setting.USER_ACCESS_TOKEN,
    #        }
    #user = requests.get('https://api.github.com/user', params=params)
    #pprint(user.json())

    #r = requests.get(user.json()['repos_url'], params=params)
    #pprint(r.json())

    # ------ TEST GithubAPI ------ #
    g = GithubAPI(setting.CLIENT_ID, setting.CLIENT_SECRET)
    print g.authorize_url()
    print g.authorize_url('read:repo_hook','gist')
