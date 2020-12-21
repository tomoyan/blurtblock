import os
from datetime import timedelta


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'YOUR_SECRET_KEY'
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
    UPVOTE_ACCOUNT = os.environ.get('UPVOTE_ACCOUNT') or 'YOUR_USERNAME'
    UPVOTE_KEY = os.environ.get('UPVOTE_KEY') or 'YOUR_PRIVATE_POSTING_KEY'

    # firebase config
    FB_APIKEY = os.environ.get('FB_APIKEY') or 'YOUR_FB_APIKEY'
    FB_AUTHDOMAIN = 'blurtdb.firebaseapp.com'
    FB_DATABASEURL = 'https://blurtdb.firebaseio.com'
    FB_STORAGEBUCKET = 'blurtdb.appspot.com'
    FB_PRIVATE_KEY_ID = os.environ.get(
        'FB_PRIVATE_KEY_ID') or 'YOUR_PRIVATE_KEY_ID'
    FB_PRIVATE_KEY = os.environ.get('FB_PRIVATE_KEY') or 'YOUR_PRIVATE_KEY'
    FB_CLIENT_EMAIL = os.environ.get('FB_CLIENT_EMAIL') or 'YOUR_CLIENT_EMAIL'
    FB_CLIENT_ID = os.environ.get('FB_CLIENT_ID') or 'YOUR_CLIENT_ID'
    FB_AUTH_PROVIDER_X509_CERT_URL = os.environ.get(
        'FB_AUTH_PROVIDER_X509_CERT_URL') or 'YOUR_AUTH_PROVIDER_X509_CERT_URL'
    FB_CLIENT_X509_CERT_URL = os.environ.get(
        'FB_CLIENT_X509_CERT_URL') or 'YOUR_CLIENT_X509_CERT_URL'
