from beem import Blurt
from beem.account import Account
from beem.comment import Comment
import pyrebase
import base64
import json
import os
import cryptocode

blurt_nodes = ['https://rpc.blurt.world']

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
            BLT = Blurt(blurt_nodes, keys=[posting])
            ACC = Account(username, blockchain_instance=BLT)
            if ACC.get_voting_power() < voting_power:
                continue

            COMMENT = Comment(
                identifier, api='condenser', blockchain_instance=BLT)
            if ACC.has_voted(COMMENT):
                print('ALREADY_VOTED', ACC, identifier)
                continue
            print(username, weight)
            BLT.vote(weight, identifier, account=ACC)
        except Exception as err:
            print('TRAIL_VOTE_ERR', username, err)


if __name__ == '__main__':
    main()
