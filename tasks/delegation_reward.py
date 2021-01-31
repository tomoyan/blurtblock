from beem import Blurt
from beem.account import Account
from beem.account import Amount
from datetime import datetime
import pyrebase
import base64
import json
import os

# Setup blurt nodes and account
blurt_nodes = ['https://rpc.blurt.world']

username = os.environ.get('USERNAME')

blurt = Blurt(blurt_nodes)
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
    budget = get_reward_budget()

    delegations = get_delegation_list()

    rewards = get_rewards(budget, delegations)

    send_rewards(rewards)
    publish_post(rewards)


def get_reward_budget():
    budget_bp = 0
    # Get 1 day curation reward in BP
    reward_bp = account.get_curation_reward(days=1)

    # 10 % of reward gets distributed
    percent = 10
    budget_bp = int(reward_bp * percent / 100)

    return budget_bp


def get_delegation_list():
    delegations = {}

    # get delegation history
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

    return delegations


def get_rewards(budget, delegations):
    rewards = dict()
    total_bp = sum(delegations.values())

    # Rewards get divided by delegation %
    for key in delegations:
        amount = (delegations[key] / total_bp) * budget
        rewards[key] = amount

    # Save reward_list into firebase
    db_name = 'daily_rewards'
    today = datetime.now().strftime("%Y-%m-%d")
    reward_list = []
    for key in rewards:
        reward_list.append(f'{key}: {rewards[key]}')

    db_prd.child(db_name).child(today).set(reward_list)

    return rewards


def send_rewards(rewards):
    active_key = os.environ.get('ACTIVE_KEY')
    b = Blurt(blurt_nodes, keys=[active_key])
    a = Account(username, blockchain_instance=b)

    # Transfer rewards to users
    for key in rewards:
        amount = f'{rewards[key]:.2f}'
        memo = f"""Hi @{key}!
    Here is your delegation reward.
    Your delegation reward is {amount} BP
    Thank you so much for your support!
    @tomoyan
        """

        # Transfer BLURT
        a.transfer(key, amount, 'BLURT', memo)


def publish_post(rewards):
    post_key = os.environ.get('POST_KEY')
    b = Blurt(blurt_nodes, keys=[post_key])

    today = datetime.now().strftime("%Y-%m-%d")
    title = f'Daily Delegation Payout - {today}'
    tags = ['blurtblock', 'delegation', 'rewards', 'blurt']

    table = """
| Delegator | Reward |
| -- | -- |
    """
    for key in rewards:
        amount = f'{rewards[key]:.2f}'
        row = f'| @{key} | {amount} BLURT |\n'
        table += row

    body = f"""
![0.png](https://images.blurt.buzz/DQmR5RgHVSuMkD7LYGV8U6n65c9uFbdkTxUnJ4VJuZPM37i/0.png)
## Everyday is a BLURT day if you delegate your BP

If you delegate your BP to @tomoyan, you will receive daily rewards.
Also, delegators will get a **BONUS** upvote.
Just use [**Free UPVOTE**](https://blurtblock.herokuapp.com/blurt/upvote/).
https://blurtblock.herokuapp.com/blurt/upvote/
Give it a try! Anybody can use it even if you don't delegate.

## Daily Rewards Today
{table}
Thank you for your support!
Have a Blurt day :)
    """

    b.post(
        author=username,
        title=title,
        body=body,
        tags=tags,
        self_vote=False)


if __name__ == '__main__':
    main()
