from beem import Blurt
from beem.account import Account
from beem.comment import Comment
import pyrebase
import base64
import json
import os
import cryptocode
import random
import requests
import time
from datetime import datetime

blurt_nodes = [
    'https://rpc.blurt.world',
    # 'https://rpc.blurt.live',
    'https://rpc.blurt.one',
    'https://blurt-rpc.saboin.com',
    'https://rpc.nerdtopia.de',
    'https://kentzz.blurt.world',
    'https://rpc.blurtlatam.com',
    'https://blurtrpc.actifit.io',
]


def get_node():
    random.shuffle(blurt_nodes)
    result = blurt_nodes[0]

    for node in blurt_nodes:
        try:
            response = requests.get(node, timeout=1)
            if response:
                result = node
                break
        except requests.exceptions.RequestException as e:
            print(f'NODE_ERR:{node} {e}')

    return result


FB_SERVICEACCOUNT = os.environ.get('FB_SERVICEACCOUNT')

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
    process_trail_vote()


def process_trail_vote():
    trail_data = get_trail_data()
    db_name = 'upvote_log'

    for data in trail_data:
        trail_upvote(
            data['value']['identifier'],
            data['value']['vote_weight'])

        db_prd.child(db_name).child(data['key']).update({
            'trail_vote': True})


def get_trail_data():
    trail_data = []
    db_name = 'upvote_log'
    logs = db_prd.child(db_name).get()

    for log in logs.each():
        key = log.key()
        value = log.val()
        if 'trail_vote' in value:
            if not value['trail_vote']:
                trail_data.append({
                    'key': key,
                    'value': value,
                })

    return trail_data


def decrypt_message(posting):
    message = cryptocode.decrypt(posting, FB_SERVICEACCOUNT)

    return message


def trail_upvote(identifier, vote_weight):
    weight = 100.0
    voting_power = 80.0
    db_name = 'trail_followers'

    followers = db_prd.child(
        db_name).order_by_child("status").equal_to(1).get()

    for follower in followers.each():
        username = follower.val()['username']
        posting = decrypt_message(follower.val()['posting'])
        # weight = vote_weight
        weight = follower.val()['weight']

        try:
            node = get_node()
            BLT = Blurt(node, keys=[posting], num_retries=3)
            ACC = Account(username, blockchain_instance=BLT)
            if ACC.get_voting_power() < voting_power:
                continue

            blurt_balance = ACC.get_balance('available', 'BLURT')
            if blurt_balance.amount < 0.1:
                print('INSUFFICIENT_BALANCE', username, blurt_balance.amount)
                # disable_trail(username)
                continue

            COMMENT = Comment(
                identifier, api='condenser', blockchain_instance=BLT)
            if ACC.has_voted(COMMENT):
                print('ALREADY_VOTED', ACC, identifier)
                continue

            print(username, weight, identifier)
            BLT.vote(weight, identifier, account=ACC)
        except Exception as err:
            print('TRAIL_VOTE_ERR', username, node, err)

        time.sleep(1)


def disable_trail(username):
    follow_key = None

    trail_data = {
        'username': username,
        'created': datetime.utcnow().strftime("%m/%d/%Y %H:%M:%S"),
        'status': 0,
    }

    db_name = 'trail_followers'

    follower = db_prd.child(db_name).order_by_child(
        "username").equal_to(username).get().val()

    if follower:
        item = next(iter(follower.items()))
        follow_key = item[0]

    if follow_key:
        db_prd.child(db_name).child(follow_key).update(trail_data)


if __name__ == '__main__':
    main()
