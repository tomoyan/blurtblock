from beem import Blurt
from beem.account import Account
import pyrebase
import base64
import json
import os
import time
from datetime import datetime
import random
import requests

# Setup blurt nodes and account
BLURT_NODES = [
    'https://rpc.blurt.world',
    'https://blurt-rpc.saboin.com',
    'https://rpc.dotwin1981.de',
    'https://rpc.nerdtopia.de',
    'https://kentzz.blurt.world',
]


def get_node():
    random.shuffle(BLURT_NODES)
    for node in BLURT_NODES:
        try:
            response = requests.get(node, timeout=1)
            if response:
                return node
        except requests.exceptions.RequestException as e:
            print(f'NODE_ERR:{node} {e}')


USERNAME = os.environ.get('USERNAME')
UPVOTE_KEY = os.environ.get('POST_KEY')
BLURT = Blurt(get_node(), keys=[UPVOTE_KEY])
ACCOUNT = Account(USERNAME, blockchain_instance=BLURT)

USERS = [
    'ecosynthesizer', 'maxinpower',
    'the-gorilla', 'tomoyan',
    'kahkashanrkploy', 'kamranrkploy',
    'famigliacurione'
]

now = datetime.utcnow()
current_time = now.strftime("%m/%d/%Y %H:%M:%S")


# Firebase configuration
serviceAccountCredentials = json.loads(
    base64.b64decode(os.environ.get('FB_SERVICEACCOUNT').encode()).decode())

firebase_config_prd = {
    "apiKey": os.environ.get('FB_APIKEY'),
    "authDomain": os.environ.get('FB_AUTHDOMAIN'),
    "databaseURL": os.environ.get('FB_DATABASEURL'),
    "storageBucket": os.environ.get('FB_STORAGEBUCKET'),
    "serviceAccount": serviceAccountCredentials,
}
firebase = pyrebase.initialize_app(firebase_config_prd)

# Get a reference to the database service
db_prd = firebase.database()


def main():
    for user in USERS:
        upvote_blog_entries_username(user)


def upvote_blog_entries_username(name):
    db_name = 'upvote_log'
    ACCT = Account(name, blockchain_instance=BLURT)
    posts = ACCT.blog_history(limit=1, reblogs=False)

    for post in posts:
        voted = ACCOUNT.has_voted(post)

        if not voted:
            identifier = post.authorperm
            weight = 85.0
            if name == 'ecosynthesizer':
                weight = 35.0
            elif name == 'kahkashanrkploy':
                weight = 50.0
            elif name == 'kamranrkploy':
                weight = 50.0

            # Upvote a post
            try:
                BLURT.vote(weight, identifier, account=ACCOUNT)
                # save upvote_data
                upvote_data = {
                    'username': name,
                    'identifier': identifier,
                    'created': current_time,
                    'vote_weight': 0.0,
                    'bonus_weight': 0.0,
                    'client_ip': '0.0.0.0',
                    'trail_vote': False
                }
                db_prd.child(db_name).push(upvote_data)
            except Exception as err:
                print('BLOG_ENTRY_VOTE_ERR', err)

            time.sleep(3)


if __name__ == '__main__':
    main()
