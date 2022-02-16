from beem import Blurt
from beem.account import Account
from beem.account import Amount
from datetime import datetime, timedelta
import pyrebase
import base64
import json
import os
import random
import requests

# Setup blurt nodes and account
blurt_nodes = [
    'https://rpc.blurt.world',
    'https://blurt-rpc.saboin.com',
    'https://rpc.tekraze.com',
    'https://rpc.dotwin1981.de',
    'https://rpc.nerdtopia.de',
    'https://kentzz.blurt.world',
]


def get_node():
    random.shuffle(blurt_nodes)
    for node in blurt_nodes:
        try:
            response = requests.get(node, timeout=1)
            if response:
                return node
        except requests.exceptions.RequestException as e:
            print(f'NODE_ERR:{node} {e}')


blurt = Blurt(get_node())

username = os.environ.get('USERNAME')
account = Account(username, blockchain_instance=blurt)

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
    # Update delegator list every hour
    # And store data into delegation_list
    update_delegation_list()

    # Clean up access_log (days: 3)
    fb_data_cleanup("access_log", 3)

    # Clean up upvote_log (days: 3)
    fb_data_cleanup("upvote_log", 3)

    # Clean up account_history (days: 1)
    fb_data_cleanup("account_history", 1)

    # Clean up upvote_count (days: 7)
    fb_data_cleanup("upvote_count", 7)

    # Clean up daily_rewards log
    daily_rewards_log_cleanup()


def update_delegation_list():
    delegations = {}

    # Get delegation history
    start = datetime(2020, 12, 30)
    ops = ['delegate_vesting_shares']
    delegate_vesting_shares = account.history(
        start=start, only_ops=ops)

    for operation in delegate_vesting_shares:
        if operation['delegator'] == username:
            continue

        if operation['vesting_shares']['amount'] == '0':
            if operation['delegator'] in delegations:
                delegations.pop(operation['delegator'])
        else:
            amount = Amount(operation['vesting_shares'])
            bp = blurt.vests_to_bp(amount)
            delegations[operation['delegator']] = {
                'bp': bp,
                'timestamp': operation['timestamp']
            }

    delegation_list = []
    for key in delegations:
        delegation_list.append({
            'username': key,
            'bp': delegations[key]['bp'],
            'timestamp': delegations[key]['timestamp'],
        })

    db_name = 'delegation_list'
    db_prd.child(db_name).child('delegators').set(delegation_list)


def fb_data_cleanup(db_name, duration):
    # Get log data
    logs = db_prd.child(db_name).get()

    datetime_old = datetime.utcnow() - timedelta(days=duration)

    # Remove old data
    for log in logs.each():
        key = log.key()
        data = log.val()

        datetime_obj = datetime.strptime(
            data["created"], "%m/%d/%Y %H:%M:%S")

        if datetime_obj < datetime_old:
            db_prd.child(db_name).child(key).remove()


def daily_rewards_log_cleanup():
    one_month = datetime.now() - timedelta(days=30)
    one_year = datetime.now() - timedelta(days=365)

    db_name = "daily_rewards"

    # Get daily_rewards log data
    logs = db_prd.child(db_name).get()
    for log in logs.each():
        key = log.key()

        datetime_obj = datetime.strptime(key, "%Y-%m-%d")

        # Delete 1 year old data
        if datetime_obj < one_year:
            db_prd.child(db_name).child(key).remove()
            continue

        # Delete 1 month old data
        # But keep 1st of the month data
        if datetime_obj < one_month and datetime_obj.day != 1:
            db_prd.child(db_name).child(key).remove()


if __name__ == '__main__':
    main()
