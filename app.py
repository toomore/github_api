# -*- coding:utf8 -*-
import setting
from flask import Flask
from flask import redirect
from flask import request
from flask import session
from flask import url_for
from github_api import GithubAPI
from uuid import uuid4


app = Flask(__name__)
app.secret_key = setting.SESSION_KEY

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
        result = u'%s' % github_api.get_api('/user')
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
    app.run(debug=True)
