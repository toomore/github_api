# -*- coding:utf8 -*-
import redis
import setting
import ujson as json
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
            return redirect(url_for('user'))

    return u'Wrong code. state: %s, %s' % (state, session['state'])

@app.route("/user")
def user():
    if 'token' in session:
        github_api = GithubAPI(setting.CLIENT_ID, setting.CLIENT_SECRET,
                session['token'])
        result = CACHE.get(u'github_api:user:%s' % session['token'])
        if not result:
            result = github_api.get_api('/user')
            if 'language' not in result:
                result['language'] = ', '.join([i for i, value in github_api.get_user_language(result['login']).most_common()])
            CACHE.set(u'github_api:user:%s' % session['token'],
                      json.dumps(result), 60)
        else:
            result = json.loads(result)
        return render_template('user.html', result=result)
    else:
        result = u'Please Login!'

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
