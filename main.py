import os
import requests
import indicoio
from flask import Flask
from flask import render_template, redirect, request


app = Flask(__name__)

clientID = "c154c63ac943405e848bf8a936eeb12a"
clientSecret = "dd9e465214994ed788ecb9781f3c460f"
grantType = "authorization_code"
redirectURI = "https://shrouded-sands-7834.herokuapp.com/get-20"
auth = "https://api.instagram.com/oauth/authorize/?" + "client_id=" + clientID + "&" + "redirect_uri=" + redirectURI + "&response_type=code"
accessToken = ""

# When user arrives at the site, redirect him/her to authorize permission to use Instagram
@app.route('/')
def hello():
    return redirect(auth)


# After user authenticates, stores the access token so we can make
# api calls and redirect the user to the landing page
@app.route('/get-20')
def get_access_token():
    code = request.args.get('code')
    result = requests.post("https://api.instagram.com/oauth/access_token", data={"client_id": clientID,
                                                                                 "client_secret": clientSecret,
                                                                                 "grant_type":"authorization_code",
                                                                                 "redirect_uri": redirectURI,
                                                                                 "code": code})
    json_result = result.json()
    global accessToken
    accessToken = json_result['access_token']
    return render_template("index.html")


# return a page of the 20 most recent posts about capital one on instagram
@app.route('/posts')
def search_posts():
    posts = get_posts()
    return render_template("posts.html", posts=posts)


# Makes a get request to the Instagram api, asking for the 20 most recent
# posts about Capital One
def get_posts():
    result = requests.get("https://api.instagram.com/v1/tags/capitalone/media/recent?count=20&access_token=" + accessToken)
    return result.json()['data']


# return the sentiment analysis summary page
@app.route('/sentiment')
def sentiment():
    posts = get_posts()
    list_caps = []
    for post in posts:
        list_caps.append(post['caption']['text'])
    sentiment_counts = sentiment_analysis(list_caps)
    return render_template("sentiment.html", sentiment=sentiment_counts)


# Takes in a list of captions of length 20. Conducts sentiment analysis on
# them by using the indicoio sentiment analysis API. The api returns a dec
# number between 0 and 1. The function returns a dictionary of the number of
# positive, neutral, and negative comments.
def sentiment_analysis(list_captions):
    indicoio.config.api_key = '64ea7c556b0060d9d7a8e97c8d8968d7'
    list_sentiment = []
    num_pos = 0
    num_neu = 0
    num_neg = 0
    for caption in list_captions:
        sentiment1 = indicoio.sentiment_hq(caption)
        list_sentiment.append(sentiment1)
        # sentiment is positive
        if sentiment > 0.55:
            num_pos += 1
        # sentiment is neutral
        elif sentiment > 0.45:
            num_neu += 1
        # sentiment is negative
        else:
            num_neg += 1

    sentiment_dict = {"positive": num_pos,
                      "neutral": num_neu,
                      "negative": num_neg}
    return sentiment_dict


# returns the user information page
@app.route('/user/<userid>')
def get_user_info(userid=None):
    user_info = requests.get("https://api.instagram.com/v1/users/" + userid + "/", params={"access_token": accessToken})
    user = user_info.json()['data']
    return render_template("user.html", user=user)

if __name__ == '__main__':
    app.run()
