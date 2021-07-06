from beem import Blurt
from beem.account import Account
from datetime import datetime
import pyrebase
import base64
import json
import os
import random

# Setup blurt nodes and account
blurt_nodes = ['https://rpc.blurt.world']

username = os.environ.get('USERNAME')

blurt = Blurt(blurt_nodes)
account = Account(username, blockchain_instance=blurt)
token_power = account.get_token_power()
token_power = f'{token_power:,.2f} BP'

# 40% of curation reward distributed
PERCENT = 40

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

    budget_bp = int(reward_bp * PERCENT / 100)

    return budget_bp


def get_delegation_list():
    delegations = dict()
    db_name = 'delegation_list'
    data = db_prd.child(db_name).child('delegators').get()

    for d in data.each():
        username = d.val()['username']
        bp = d.val()['bp']
        delegations[username] = bp

    return delegations


def get_top_leaderboard():
    members = {}
    top_ten_members = []
    count = 10
    db_name = 'upvote_log'
    logs = db_prd.child(db_name).get()

    for log in logs.each():
        value = log.val()
        username = value['username']
        vote_weight = value['vote_weight']

        if username in members:
            members[username] += vote_weight
        else:
            members[username] = vote_weight

    members = dict(sorted(
        members.items(), reverse=True,
        key=lambda item: item[1]))

    # Find top 10 members
    for i, key in enumerate(members):
        if i == count:
            break
        top_ten_members.append(key)

    return top_ten_members


def get_rewards(budget, delegations):
    rewards = dict()
    total_bp = sum(delegations.values())

    # top_members = get_top_leaderboard()

    # Rewards get divided by delegation %
    for key in delegations:
        # Base amount
        amount = (delegations[key] / total_bp) * budget

        if amount < 0.01:
            continue

        # top_leaderboard will get 30% bonus
        # if key in top_members:
        #     amount += amount * 0.3

        rewards[key] = amount

    # Save reward_list into firebase
    db_name = 'daily_rewards'
    today = datetime.now().strftime("%Y-%m-%d")
    reward_list = [f'Budget: {budget}']
    for key in rewards:
        reward_list.append(f'{key}: {rewards[key]}')

    db_prd.child(db_name).child(today).set(reward_list)

    return rewards


def send_rewards(rewards):
    active_key = os.environ.get('ACTIVE_KEY')
    b = Blurt(blurt_nodes, keys=[active_key])
    a = Account(username, blockchain_instance=b)

    db_name = 'failed_transfer'
    today = datetime.now().strftime("%Y-%m-%d")

    # Transfer rewards to users
    for key in rewards:
        amount = f'{rewards[key]:.2f}'
        memo = f"""Hi @{key}!
    Here is your delegation reward {amount} BLURT.
    Thank you so much for your support!
    @tomoyan
        """

        try:
            # Transfer BLURT
            a.transfer(key, amount, 'BLURT', memo)
        except Exception as err:
            # save failed transaction into fb
            error_data = {
                'date': today,
                'username': key,
                'amount': amount,
                'error': err,
            }
            db_prd.child(db_name).push(error_data)


def fb_get_main_image():
    # Get images from fb post_images
    # and return one random image
    # Default image
    main_image = 'https://i.imgur.com/4VuswjQ.png'
    main_images = []
    db_name = "post_images"
    all_images = db_prd.child(db_name).get()

    for image in all_images.each():
        main_images.append(image.val())

    main_image = random.choice(main_images)
    return main_image


def publish_post(rewards):
    post_key = os.environ.get('POST_KEY')
    b = Blurt(blurt_nodes, keys=[post_key])

    today = datetime.now().strftime("%Y-%m-%d")
    title = f'Daily Delegation Payout - {today}'
    tags = ['blurtblock', 'delegation', 'rewards', 'blurt']
    base_url = 'https://blurt.blog'
    permalink = '@tomoyan/how-to-blurt-passive-income-daily-payout-report'
    post_url = f'{base_url}/{permalink}'
    leaderboard = 'https://blurtblock.herokuapp.com/blurt/leaderboard'

    main_img = fb_get_main_image()

    table = """
| Delegator | Reward |
| -- | -- |
    """
    for key in rewards:
        amount = f'{rewards[key]:.2f}'
        row = f'| @{key} | {amount} BLURT |\n'
        table += row

    body = f"""
![0.png]({main_img})
## Effective Blurt Power: {token_power}
## Everyday is a BLURT day if you delegate your BP

**Star Bonus**: You will receive stars for using upvote.
5 Stars - guarantee 100%
2.5 Starts - 25% + regular vote%
![](https://i.imgur.com/IHZYaWx.png)
The more you use, the more you earn!
https://blurtblock.herokuapp.com

Top 3 [**Leaderboard**]({leaderboard}) members will receive bonus **UPVOTE**
* Top 1 will receive **100%** UPVOTE
* Top 2 will receive regular vote + **50%** (+ delegation bonus)
* Top 3 will receive regular vote + **25%** (+ delegation bonus)

Delegation Bonus 👇
If you delegate your BP to @tomoyan, you will receive daily rewards.
Also, delegators will get a **BONUS** upvote.
Just use [**Free UPVOTE**](https://blurtblock.herokuapp.com/blurt/upvote/).
https://blurtblock.herokuapp.com/blurt/upvote
Give it a try! Anybody can use it even if you don't delegate.

## Daily Rewards Today
{table}

## How to delegate BLURT POWER(BP)? Here 👇
[Blurt Passive Income: Delegation]({post_url})
{post_url}

Thank you for your support!
Have a Blurt Day :)
<center>

**BLURT for You**
![qrcode_blurtblock.herokuapp.com.png](https://i.imgur.com/Z2AXZle.png)

</center>

    """

    b.post(
        author=username,
        title=title,
        body=body,
        tags=tags,
        self_vote=False)


if __name__ == '__main__':
    main()
