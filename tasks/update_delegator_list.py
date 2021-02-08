from beem import Blurt
from beem.account import Account
from beem.account import Amount
from datetime import datetime, timedelta
import pyrebase
import base64
import json
import os

# Setup blurt nodes and account
blurt_nodes = [
    'https://rpc.blurt.world',
]
blurt = Blurt(blurt_nodes)

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
    # Update delegator list once a day
    # And store data into delegation_list
    update_delegation_list()

    # Clean up access_log (1 days)
    fb_data_cleanup("access_log", 1)

    # Clean up upvote_log (7 days)
    fb_data_cleanup("upvote_log", 7)


def update_delegation_list():
    delegations = {}

    # Get delegation history
    delegate_vesting_shares = account.history(
        only_ops=["delegate_vesting_shares"])

    for operation in delegate_vesting_shares:
        if operation['delegator'] == username:
            continue

        if operation['vesting_shares']['amount'] == '0':
            delegations.pop(operation['delegator'])
        else:
            amount = Amount(operation['vesting_shares'])
            bp = blurt.vests_to_bp(amount)
            delegations[operation['delegator']] = bp

    delegation_list = []
    for key in delegations:
        delegation_list.append({
            'username': key,
            'bp': delegations[key],
        })

    db_name = 'delegation_list'
    db_prd.child(db_name).child('list').set(delegation_list)


def fb_data_cleanup(db_name, duration):
    # Get log data
    logs = db_prd.child(db_name).get()

    datetime_old = datetime.now() - timedelta(days=duration)

    # Remove old data
    for log in logs.each():
        key = log.key()
        data = log.val()

        datetime_obj = datetime.strptime(
            data["created"], "%m/%d/%Y %H:%M:%S")

        if datetime_obj < datetime_old:
            db_prd.child(db_name).child(key).remove()


if __name__ == '__main__':
    main()