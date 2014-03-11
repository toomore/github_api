# -*- coding:utf8 -*-
import requests
import setting
import ujson as json
from urlparse import urljoin
from uuid import uuid4


class GithubAPI(object):
    def __init__(self, client_id, client_secret, token=None):
        self.api_url = 'https://api.github.com/'
        self.client_id = client_id
        self.client_secret = client_secret
        self.headers = {'Accept': 'application/vnd.github.v3+json'}
        self.session = requests.Session()
        self.token = token

    def __repr__(self):
        return u'<GithubAPI client_id: %s, client_secret: %s, token: %s>' % \
                (self.client_id[:7],
                 self.client_secret[:7],
                 self.token[:7] if self.token else None)

    def authorize_url(self, state=None, *scope):
        if not state:
            state = uuid4().hex

        url = 'https://github.com/login/oauth/authorize' + \
                '?client_id=%s&state=%s' % (self.client_id, state)

        if scope:
            url = url + '&scope=' + ','.join(scope)

        return url

    def access_token(self, code, redirect_uri=None):
        url = 'https://github.com/login/oauth/access_token'
        headers = {'Accept': 'application/json'}
        data = {'client_id': self.client_id,
                'client_secret': self.client_secret,
                'code': code}

        if redirect_uri:
            data['redirect_uri'] = redirect_uri

        result = requests.post(url, data=data, headers=headers).json()

        if 'access_token' in result:
            self.token = result['access_token']

        return result

    def get_api(self, path, params=None):
        return self._requests('GET', path, params)

    def patch_api(self, path, params=None):
        return self._requests('PATCH', path, params)

    def _requests(self, method, path, params=None):
        self.headers['Authorization'] = 'token %s' % self.token

        if method == 'GET':
            result = self.session.get(urljoin(self.api_url, path),
                    params=params, headers=self.headers)
        elif method == 'PATCH':
            result = self.session.patch(urljoin(self.api_url, path),
                    data=json.dumps(params), headers=self.headers)

        return result.json()

if __name__ == '__main__':
    from pprint import pprint
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
    print g.authorize_url(None, 'read:repo_hook','gist', 'user')
    #print g.access_token('d92ecf94496c6811e677')
    g.token = setting.USER_ACCESS_TOKEN
    pprint(g.get_api('/user'))
    pprint(g.get_api('/rate_limit'))
    #pprint(g.patch_api('user', {'bio': 'I love Python.'}))
    pprint(g.get_api('/user/emails'))
    #for i in g.get_api('/users?since=222'):
    #    if i['site_admin']:
    #        print i['id'], i['html_url']
    #pprint(g.get_api('/users/toomore'))
    #pprint(g.get_api('/user/repos'))

    # ------ TEST Get User Language ------ #
    from collections import Counter
    g = GithubAPI(setting.CLIENT_ID, setting.CLIENT_SECRET,
            setting.USER_ACCESS_TOKEN)
    result = g.get_api('/user/repos')
    repos = [(i['name'], i['owner']['login'], i['fork']) for i in result]
    languages = Counter()
    for no, data in enumerate(repos):
        repo, owner, fork = data
        if not fork and owner == 'toomore':
            feeds = g.get_api('/repos/%s/%s/languages' % (owner, repo))
            print no, repo, owner, feeds
            languages.update(feeds)
    pprint(languages)
