# -*- coding:utf8 -*-
import setting
from flask import Flask
from flask import redirect
from flask import request
from flask import session
from flask import url_for
from github_api import GithubAPI

app = Flask(__name__)
app.secret_key = setting.SESSION_KEY

@app.route("/login")
def login():
    github_api = GithubAPI(setting.CLIENT_ID, setting.CLIENT_SECRET)
    return redirect(github_api.authorize_url())

@app.route("/token")
def github_api_token():
    code = request.args.get('code')
    state = request.args.get('state')
    #return u'%s %s' % (code, state)
    github_api = GithubAPI(setting.CLIENT_ID, setting.CLIENT_SECRET)
    result = github_api.access_token(code)

    if 'access_token' in result:
        session['token'] = result['access_token']
        return redirect(url_for('user'))
    else:
        return u'Wrong code.'

@app.route("/user")
def user():
    if 'token' in session:
        github_api = GithubAPI(setting.CLIENT_ID, setting.CLIENT_SECRET,
                session['token'])
        result = u'%s' % github_api.get_api('user')
    else:
        result = u'Please Login!'

    return result

if __name__ == '__main__':
    app.run(debug=True)
