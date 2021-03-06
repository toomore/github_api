# -*- coding:utf8 -*-
import redis
import setting
import ujson as json
from collections import Counter
from flask import Flask
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for
from github_api import GithubAPI
from uuid import uuid4


app = Flask(__name__)
app.secret_key = setting.SESSION_KEY

CACHE = redis.StrictRedis(host=setting.REDIS_HOST,
                          port=setting.REDIS_POST,
                          db=0)

@app.template_filter('most_common')
def most_common(data, n=None):
    if isinstance(data, basestring):
        data = json.loads(data)

    data = Counter(data)
    return [language for language, value in data.most_common(n)]

@app.route("/")
def home():
    return u'<a href="%s">Login</a>' % url_for('login')

@app.route("/login")
def login():
    session['state'] = uuid4().hex
    github_api = GithubAPI(setting.CLIENT_ID, setting.CLIENT_SECRET)
    return redirect(github_api.authorize_url(session['state'], 'user'))

@app.route("/token")
def github_api_token():
    code = request.args.get('code')
    state = request.args.get('state')
    #return u'%s %s' % (code, state)

    if state == session['state']:
        github_api = GithubAPI(setting.CLIENT_ID, setting.CLIENT_SECRET)
        result = github_api.access_token(code)

        if 'access_token' in result:
            session['token'] = result['access_token']
            data = render_user_data()
            session['name'] = data['login']
            CACHE.sadd('tokenlist', '%s:%s' % (data['login'],
                                               result['access_token']))
            return redirect(url_for('user', name=session['name']))

    return u'Wrong code. state: %s, %s' % (state, session['state'])

def render_user_data(name=None, find_language=False):
    github_api = GithubAPI(setting.CLIENT_ID, setting.CLIENT_SECRET,
            session['token'])
    if name:
        key_name = u'github_api:user:%s' % name
    else:
        key_name = u'github_api:user:auth:%s' % session['token']

    result = CACHE.get(key_name)

    if not result:
        if name:
            result = github_api.get_api('/users/%s' % name)
        else:
            result = github_api.get_api('/user')

        language_key_name = 'github_api:user:language:%s' % (name if name else session['token'])

        if find_language:
            user_language = CACHE.get(language_key_name)
            if not user_language and 'language' not in result:
                #result['language'] = ', '.join([i for i, value in github_api.get_user_language(result['login']).most_common()])
                result['language'] = json.dumps(github_api.get_user_language(result['login']))
                CACHE.set(language_key_name, result['language'], 60*60)
            else:
                result['language'] = json.loads(user_language)

        if name:
            #user following
            result['following_list'] = github_api.get_api('/users/%s/following?per_page=%s' % (name, result['following']))
            result['followers_list'] = github_api.get_api('/users/%s/followers?per_page=%s' % (name, result['followers']))
            #user repos
            result['repos_list'] = github_api.get_api('/users/%s/repos?per_page=%s&sort=updated' % \
                    (name, result['public_repos']))
        else:
            #user following
            result['following_list'] = github_api.get_api('/user/following?per_page=%s' % result['following'])
            result['followers_list'] = github_api.get_api('/user/followers?per_page=%s' % result['followers'])
            #user repos
            result['repos_list'] = github_api.get_api('/user/repos?per_page=%s&sort=updated' % result['public_repos'])

        CACHE.set(key_name, json.dumps(result), 60)
    else:
        result = json.loads(result)

    return result

@app.route("/user", defaults={'name': None})
@app.route("/user/", defaults={'name': None})
@app.route("/user/<name>")
def user(name):
    if name is None:  ## No 'None' account id in github.[safe]
        if 'name' in session:
            return redirect(url_for('user', name=session['name']))
        else:
            return redirect(url_for('login'))

    if 'token' in session:
        if name == session['name']:
            result = render_user_data(find_language=True)
        else:
            result = render_user_data(name, True)

        if name != result['login']:
            return redirect(url_for('user', name=result['login']))

        return render_template('user.html', result=result)
    else:
        #return redirect(url_for('login'))
        result = u'Please <a href="/user">Login!</a>'

    return result

@app.route("/viewtoken")
def viewtoken():
    github_api = GithubAPI(setting.CLIENT_ID, setting.CLIENT_SECRET)
    return u'%s' % github_api

@app.route("/user/hireable", methods=['GET', 'POST'])
def hireable():
    if 'token' not in session:
        return u'Please Login!'

    if request.method == 'GET':
        return u'''
        <form method="POST">
            <input type="submit">
        </form>
        '''
    elif request.method == 'POST':
        github_api = GithubAPI(setting.CLIENT_ID, setting.CLIENT_SECRET,
                session['token'])
        github_api.patch_api('/user', {'hireable': True})
        return redirect(url_for('user'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
