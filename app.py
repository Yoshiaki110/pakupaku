# -*- coding: utf-8 -*-

# https://tech-blog.cloud-config.jp/2021-12-11-make-flask-app-on-azure-app-service/


import os
import tweepy
from flask import Flask, redirect, render_template, request, jsonify, make_response
import base64
import uuid
from PIL import Image
from io import BytesIO

app = Flask(__name__)

CONSUMER_KEY = os.environ['CONSUMER_KEY']           # API Key
CONSUMER_SECRET = os.environ['CONSUMER_SECRET']     # API Key Secret
CALLBACK_URL = os.environ['CALLBACK_URL']           # デプロイURL
app.config['SECRET_KEY'] = os.urandom(24)
AUTH_TBL = {}

def tweet(auth, msg, imgfile):
    api = tweepy.API(auth)
    media_ids = []
    img = api.media_upload(imgfile)
    media_ids.append(img.media_id)
    api.update_status(status=msg, media_ids=media_ids)
    print('** tweet **', msg)

@app.route('/', methods=['GET', 'POST'])
def index():
    print("** /  " + request.method)
    uid = request.cookies.get('uid', None)
    if not uid:
        uid = str(str(uuid.uuid4()))
    if request.method == 'GET':
        oauth_token = request.args.get('oauth_token', default = None, type=str)
        print("oauth_token : ", oauth_token)
        oauth_verifier = request.args.get('oauth_verifier', default = None, type=str)
        print("oauth_verifier : ", oauth_verifier)
        if oauth_token == None:
            # 未ログイン
            resp = make_response(render_template("index.html", isAuthed = False, uid = uid))
            resp.set_cookie('uid', uid)
            return resp
        # ログイン済み
        try:
            auth = AUTH_TBL[uid]
            auth.request_token['oauth_token_secret'] = oauth_verifier
            auth.get_access_token(oauth_verifier)
        except Exception as e:
            return ''' <p>エラー</p> '''
        resp = make_response(render_template("index.html", isAuthed = True, uid = uid))
        resp.set_cookie('uid', uid)
        return resp

    elif request.method == 'POST':
        try:
            auth = AUTH_TBL[uid]
        except:
            # セッションが切れた場合
            print('セッションが切れた', uid)
            resp = make_response(render_template("index.html", isAuthed = False, uid = uid))
            resp.set_cookie('uid', uid)
            return resp
        auth.set_access_token(auth.access_token, auth.access_token_secret)
        msg = request.form["msg"]
        imgfile = "./static/img/photochi.png"
        tweet(auth, msg, imgfile)

        resp = make_response(render_template("index.html", isAuthed = True, uid = uid))
        resp.set_cookie('uid', uid)
        return resp

@app.route('/twitter_auth', methods=['GET'])
def twitter_auth():
    print("** /twitter_auth")
    uid = request.cookies.get('uid', None)
    if not uid:
        uid = str(str(uuid.uuid4()))
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET, CALLBACK_URL)
    AUTH_TBL[uid] = auth
    redirect_url = auth.get_authorization_url()
    print("redirect_url : ", redirect_url)
    return redirect(redirect_url)

# トップページ
@app.route('/pakupaku')
def pakupaku():
    print("** /pakupaku")
    return render_template('pakupaku.html')

@app.route("/api/tweet", methods=['POST'])
def api_tweet():
    print("** /api/tweet start")
    base64_png = request.form['image']
    code = base64.b64decode(base64_png.split(',')[1])  # remove header
    image_decoded = Image.open(BytesIO(code))
    fname = os.path.join('./', str(str(uuid.uuid4())) + '.png')
    image_decoded.save(fname)

    os.remove(fname)
    print("** /api/tweet end")
    return jsonify({})

if __name__ == '__main__':
  app.run(debug=True)

