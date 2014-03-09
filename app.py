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
github_api = GithubAPI(setting.CLIENT_ID, setting.CLIENT_SECRET)

@app.route("/login")
def login():
    session['state'] = uuid4().hex
    return redirect(github_api.authorize_url(session['state']))

@app.route("/token")
def github_api_token():
    code = request.args.get('code')
    state = request.args.get('state')
    #return u'%s %s' % (code, state)

    if state == session['state']:
        result = github_api.access_token(code)

        if 'access_token' in result:
            session['token'] = result['access_token']
            return redirect(url_for('user'))

    return u'Wrong code. state: %s, %s' % (state, session['state'])

@app.route("/user")
def user():
    if 'token' in session:
        github_api.token = session['token']
        result = u'%s' % github_api.get_api('/user')
    else:
        result = u'Please Login!'

    return result

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
        github_api.token = session['token']
        github_api.patch_api('/user', {'hireable': True})
        return redirect(url_for('user'))

if __name__ == '__main__':
    app.run(debug=True)
