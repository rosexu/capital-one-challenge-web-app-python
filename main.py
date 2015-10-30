import os
import requests
import indicoio
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
def search_posts():
    posts = get_posts()
    return render_template("posts.html", posts=posts)


def get_posts():
    print accessToken
    result = requests.get("https://api.instagram.com/v1/tags/capitalone/media/recent?count=20&access_token=" + accessToken)
    return result.json()['data']


@app.route('/sentiment')
def sentiment():
    posts = get_posts()
    list_caps = []
    for post in posts:
        print(post['caption']['text'])
        list_caps.append(post['caption']['text'])
    sentiment_counts = sentiment_analysis(list_caps)
    return render_template("sentiment.html", sentiment=sentiment_counts)



def sentiment_analysis(list_captions):
    indicoio.config.api_key = '64ea7c556b0060d9d7a8e97c8d8968d7'
    list_sentiment = []
    num_pos = 0
    num_neu = 0
    num_neg = 0
    for caption in list_captions:
        sentiment = indicoio.sentiment_hq(caption)
        list_sentiment.append(sentiment)
        if sentiment > 0.55:
            print("positive")
            num_pos += 1
        elif sentiment > 0.45:
            print("neutral")
            num_neu += 1
        else:
            print("negative")
            num_neg += 1

    sentiment_dict = {"positive": num_pos,
                      "neutral": num_neu,
                      "negative": num_neg}
    return sentiment_dict


@app.route('/user/<userid>')
def getUserInfo(userid=None):
    print userid
    user_info = requests.get("https://api.instagram.com/v1/users/" + userid + "/", params={"access_token": accessToken})
    user = user_info.json()['data']
    return render_template("user.html", user=user)

if __name__ == '__main__':
    app.run()