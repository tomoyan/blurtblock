# from beem import Blurt
# from beem.account import Account
import pyrebase
import base64
import json
import os
from datetime import datetime
# import random
import requests

# Setup blurt nodes and account
# blurt_nodes = [
#     'https://rpc.blurt.world',
#     'https://rpc.blurt.live',
#     'https://rpc.blurt.one',
#     'https://blurt-rpc.saboin.com',
#     'https://kentzz.blurt.world',
#     'https://rpc.blurtlatam.com',
#     'https://blurtrpc.actifit.io',
# ]


# def get_node():
#     result = blurt_nodes[0]
#     random.shuffle(blurt_nodes)

#     for node in blurt_nodes:
#         try:
#             response = requests.get(node, timeout=0.5)
#             if response:
#                 result = node
#                 break
#         except requests.exceptions.RequestException as e:
#             print(f'NODE_ERR:{node} {e}')

#     return result


# USERNAME = os.environ.get('USERNAME')
# UPVOTE_KEY = os.environ.get('POST_KEY')
# BLURT = Blurt(get_node(), keys=[UPVOTE_KEY], num_retries=3)
# ACCOUNT = Account(USERNAME, blockchain_instance=BLURT)


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
    print('UPDATE_COAL_START')

    import_coal_file()

    print('UPDATE_COAL_END')


def is_coal(username=''):
    print('IS_COAL:', username)
    result = False
    db_name = 'coal_list'

    coal = db_prd.child(
        db_name).order_by_child("username").equal_to(username).get().val()
    # print(len(coal))
    if len(coal):
        result = True

    print('COAL_RESULT:', result)
    return result


def add_to_coal_list(username=''):
    print("ADD_TO_COAL_LIST", username)
    # add username to a coal_list
    if is_coal(username):
        print('Already coaled')
        return

    db_name = "coal_list"
    now = datetime.utcnow()
    current_time = now.strftime("%m/%d/%Y %H:%M:%S")

    data = {
        "username": username,
        "created": current_time,
    }

    result = db_prd.child(db_name).push(data)
    print("SAVE_RESULT ", result)


def import_coal_file():
    print('IMPORT_COAL_FILE')

    # access coal raw file
    base_url = 'https://gitlab.com'
    url = (
        f'{base_url}'
        '/blurt/openblurt/coal/-/raw/master/coal.json'
    )

    response = requests.get(url)
    coal_json = response.json()

    for username in coal_json:
        print(f'{username=}')
        # add_to_coal_list(username)


if __name__ == '__main__':
    main()
