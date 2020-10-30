import os


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or '@5b1c-8a23-7875-c70a-302a'
