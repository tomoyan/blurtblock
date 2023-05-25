import os
from datetime import timedelta


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'YOUR_SECRET_KEY'
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
    UPVOTE_ACCOUNT = os.environ.get('UPVOTE_ACCOUNT') or 'YOUR_USERNAME'
    UPVOTE_KEY = os.environ.get('UPVOTE_KEY') or 'YOUR_PRIVATE_POSTING_KEY'
    MSG_APIKEY = os.environ.get('MSG_APIKEY') or 'YOUR_MSG_APIKEY'

    # firebase config
    FB_APIKEY = os.environ.get('FB_APIKEY') or 'YOUR_FB_APIKEY'
    FB_AUTHDOMAIN = 'blurtdb.firebaseapp.com'
    FB_DATABASEURL = 'https://blurtdb.firebaseio.com'
    FB_STORAGEBUCKET = 'blurtdb.appspot.com'
    FB_SERVICEACCOUNT = os.environ.get(
        'FB_SERVICEACCOUNT') or 'FB_SERVICEACCOUNT'

    # Blurt Node list
    NODE_LIST = [
        'https://rpc.blurt.world',
        # 'https://rpc.blurt.live',
        'https://rpc.blurt.one',
        'https://blurt-rpc.saboin.com',
        # 'https://kentzz.blurt.world',
        # 'https://blurtrpc.actifit.io',
    ]
