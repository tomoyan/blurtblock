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
    update_delegator_list()

    # Clean up access_log (1 days)
    fb_data_cleanup("access_log", 1)

    # Clean up upvote_log (7 days)
    fb_data_cleanup("upvote_log", 7)


def update_delegator_list():
    username = os.environ.get('UPVOTE_ACCOUNT')
    blurt_account = Account(username, blockchain_instance=blurt)

    # Get delegation history
    delegate_vesting_shares = blurt_account.history(
        only_ops=["delegate_vesting_shares"])

    delegation_list = dict()
    for operation in delegate_vesting_shares:
        if operation['delegator'] == username:
            continue

        bp = vests_to_bp(operation['vesting_shares'])
        bp = f'{bp}'
        delegation_list[operation['delegator']] = bp

    # remove amount 0
    delegators = []
    for key in delegation_list:
        if delegation_list[key] == '0.0':
            continue
        delegators.append(key)

    # Save delegators into firebase
    db_name = 'delegators'
    db_prd.child(db_name).push(delegators)

    db_name = 'delegation_list'
    db_prd.child(db_name).push(delegation_list)


def vests_to_bp(vests):
    # VESTS to BP conversion
    bp = 0.000
    v = Amount(vests)
    bp = blurt.vests_to_bp(v)

    return bp


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
