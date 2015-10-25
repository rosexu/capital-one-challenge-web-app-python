import os
import requests
from flask import Flask
from flask import render_template, redirect, request


app = Flask(__name__)

clientID = "c154c63ac943405e848bf8a936eeb12a"
clientSecret = "dd9e465214994ed788ecb9781f3c460f"
grantType = "authorization_code"
redirectURI = "http://localhost:5000/get-20"
auth = "https://api.instagram.com/oauth/authorize/?" + "client_id=" + clientID + "&" + "redirect_uri=" +redirectURI + "&response_type=code"
accessToken = ""


@app.route('/')
def hello():
    return redirect(auth)


@app.route('/get-20')
def getPosts():
    code = request.args.get('code')
    result = requests.post("https://api.instagram.com/oauth/access_token", data = {"client_id":clientID,
                                                                                   "client_secret":clientSecret,
                                                                                   "grant_type":"authorization_code",
                                                                                   "redirect_uri":redirectURI,
                                                                                   "code":code})
    jsonResult = result.json()
    global accessToken
    accessToken = jsonResult['access_token']
    return render_template("index.html")


@app.route('/posts')
def searchPosts():
    print accessToken
    result = requests.get("https://api.instagram.com/v1/tags/capitalone/media/recent?count=20&access_token=" + accessToken)
    posts = result.json()['data']
    return render_template("posts.html", posts=posts)


@app.route('/user/<userid>')
def getUserInfo(userid=None):
    print userid
    user_info = requests.get("https://api.instagram.com/v1/users/" + userid + "/", params={"access_token": accessToken})
    user = user_info.json()['data']
    return render_template("user.html", user=user)

if __name__ == '__main__':
    app.run()