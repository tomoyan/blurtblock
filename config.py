import os
from datetime import timedelta


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'YOUR_SECRET_KEY'
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
    UPVOTE_ACCOUNT = os.environ.get('UPVOTE_ACCOUNT') or 'YOUR_USERNAME'
    UPVOTE_KEY = os.environ.get('UPVOTE_KEY') or 'YOUR_PRIVATE_POSTING_KEY'
    FB_APIKEY = os.environ.get('FB_APIKEY') or 'YOUR_FB_APIKEY'
