from beem import Blurt
from beem.account import Account
import concurrent.futures
from datetime import datetime, date
import pyrebase
import base64
import json
import os
import random

# Setup blurt nodes and account
BLURT_NODES = ['https://rpc.blurt.world']
PKEY = os.environ.get('POST_KEY')
AKEY = os.environ.get('ACTIVE_KEY')
BLURT = Blurt(BLURT_NODES, keys=[PKEY, AKEY])

USERNAME = os.environ.get('USERNAME')
ACCOUNT = Account(USERNAME, blockchain_instance=BLURT)
# 35% of curation reward is distributed
PERCENT = 35

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


def get_reward_budget():
    budget_bp = 0
    # Get 1 day curation reward in BP
    reward_bp = ACCOUNT.get_curation_reward(days=1)

    budget_bp = int(reward_bp * PERCENT / 100)

    return budget_bp


def get_delegation_list():
    delegations = dict()
    db_name = 'delegation_list'
    data = db_prd.child(db_name).child('list').get()

    for d in data.each():
        username = d.val()['username']
        bp = d.val()['bp']
        delegations[username] = bp

    return delegations


def get_rewards(budget, delegations):
    rewards = [{'username': 'Budget', 'amount': budget}]
    total_bp = sum(delegations.values())

    # reward budget is divided and
    # each delegator will receive their cut
    for key in delegations:
        amount = (delegations[key] / total_bp) * budget

        if amount < 0.01:
            continue

        # rewards[key] = amount
        rewards.append({'username': key, 'amount': amount})

    # Save rewards list into firebase
    db_name = 'daily_rewards'
    today = date.today()
    db_prd.child(db_name).child(today).set(rewards)

    return rewards


def send_rewards(data):
    username = data['username']
    amount = f'{data["amount"]:.2f}'

    memo = f"""Hi @{username}!
    Here is your delegation reward {amount} BLURT.
    Thank you so much for your support!
    @tomoyan
    """

    # Transfer BLURT
    result = ACCOUNT.transfer(username, amount, 'BLURT', memo)

    return result


def publish_post(rewards):
    today = date.today()
    title = f'Daily Delegation Payout - {today}'
    tags = ['blurtblock', 'delegation', 'rewards', 'blurt']
    blurt_url = 'https://blurtter.com'
    permalink = '@tomoyan/how-to-blurt-passive-income-daily-payout-report'
    post_url = f'{blurt_url}/{permalink}'
    leaderboard = 'https://blurtblock.herokuapp.com/blurt/leaderboard'
    main_images = [
        'https://i.imgur.com/HxC5git.png',
        'https://i.imgur.com/7CPR2cY.jpg',
        'https://i.imgur.com/jGD8bHf.jpg',
        'https://i.imgur.com/xxMp09Z.jpg',
        'https://i.imgur.com/7ugZMN5.jpg',
        'https://i.imgur.com/SS2v5ag.jpg',
        'https://i.imgur.com/gvWGvLY.jpg',
        'https://i.imgur.com/xv2nitI.jpg',
        'https://i.imgur.com/DClQRLP.jpg',
        'https://i.imgur.com/MABed6f.jpg',
        'https://i.imgur.com/LSUzP36.jpg',
        'https://i.imgur.com/ygK7jw0.jpg',
        'https://i.imgur.com/viM3Utt.jpg',
        'https://i.imgur.com/PNnWGBv.jpg',
        'https://i.imgur.com/wLT9MyB.jpg',
        'https://i.imgur.com/ccn9EGT.jpg',
        'https://i.imgur.com/IvvDS81.jpg',
        'https://i.imgur.com/p3QeamK.jpg'
    ]
    main_img = random.choice(main_images)

    table = """
| Delegator | Reward |
| -- | -- |
    """

    for reward in rewards:
        amount = f'{reward["amount"]:.2f}'
        row = f'| @{reward["username"]} | {amount} BLURT |\n'
        table += row

    body = f"""
![0.png]({main_img})
## Everyday is a BLURT day if you delegate your BP

Top 3 [**Leaderboard**]({leaderboard}) members will receive bonus **UPVOTE**
* Top 1 will receive **100%** UPVOTE
* Top 2 will receive regular vote + **50%** (+ delegation bonus)
* Top 3 will receive regular vote + **25%** (+ delegation bonus)

Delegation Bonus 👇
If you delegate your BP to @tomoyan, you will receive daily rewards.
Also, delegators will get a **BONUS** upvote.
Just use [**Free UPVOTE**](https://blurtblock.herokuapp.com/blurt/upvote/).
https://blurtblock.herokuapp.com/blurt/upvote/
Give it a try! Anybody can use it even if you don't delegate.

## Daily Rewards Today
{table}

## How to delegate BLURT POWER(BP)? Here 👇
[Blurt Passive Income: Delegation]({post_url})
{post_url}

Thank you for your support!
Have a Blurt day :)
<center>

**BLURT for You**
![qrcode_blurtblock.herokuapp.com.png](https://i.imgur.com/Z2AXZle.png)

</center>

    """

    BLURT.post(
        author=USERNAME,
        title=title,
        body=body,
        tags=tags,
        self_vote=False)


def main():
    # get reward budget in BP
    budget = get_reward_budget()

    # username and BPs in dict
    # {'annas58': 3507.4396800131894}
    delegations = get_delegation_list()

    # username: BLURT amounts in list
    # [{'amount': 1.3052248323206166, 'username': 'luciannagy'},{}]
    rewards = get_rewards(budget, delegations)

    # send rewards concurrently
    db_name = 'failed_transfer'
    now = datetime.utcnow()
    created = now.strftime("%m/%d/%Y %H:%M:%S")

    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = executor.map(send_rewards, rewards)

        for result in results:
            try:
                print(result)
            except Exception as err:
                # save failed transaction into fb
                error_data = {
                    'created': created,
                    'error': err,
                }
                db_prd.child(db_name).push(error_data)

    # create a report and post it
    publish_post(rewards)


if __name__ == '__main__':
    main()
