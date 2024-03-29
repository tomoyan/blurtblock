from beem import Blurt
from beem.account import Account
from datetime import datetime
import pyrebase
import base64
import json
import os
import random
import requests

# Setup blurt nodes and account
blurt_nodes = [
    'https://rpc.blurt.world',
    # 'https://rpc.blurt.one',
    # 'https://blurt-rpc.saboin.com',
    # 'https://rpc.blurt.live',
    # 'https://kentzz.blurt.world',
    # 'https://rpc.blurtlatam.com',
    # 'https://blurtrpc.actifit.io',
]


def get_node():
    result = blurt_nodes[0]
    random.shuffle(blurt_nodes)

    for node in blurt_nodes:
        try:
            response = requests.get(node, timeout=0.5)
            if response:
                result = node
                break
        except requests.exceptions.RequestException as e:
            print(f'NODE_ERR:{node} {e}')

    print('NODE', result)
    return result


username = os.environ.get('USERNAME')
INVESTOR = os.environ.get('INVESTOR')

blurt = Blurt(get_node(), num_retries=3)
account = Account(username, blockchain_instance=blurt)
token_power = account.get_token_power()
token_power = f'{token_power:,.2f} BP'

# 25% of curation reward distributed
PERCENT = 25

REWARD_MINIMUM = 0.1

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
    print('Start delegation_reward')

    print('GET_REWARD_BUDGET')
    budget = get_reward_budget()

    print('GET_DELEGATION_LIST')
    delegations = get_delegation_list()

    print('GET_REWARDS')
    rewards = get_rewards(budget, delegations)

    print('SEND_REWARDS')
    send_rewards(rewards)

    print('PUBLISH_POST')
    publish_post(rewards)

    print('End delegation_reward')


def inv_tx(reward_bp):
    db_name = 'inv_transaction'
    today = datetime.now().strftime("%Y-%m-%d")
    ratio = int(os.environ.get('INV_RATIO'))
    active_key = os.environ.get('ACTIVE_KEY')
    blt = Blurt(get_node(), keys=[active_key])
    acc = Account(username, blockchain_instance=blt)

    investor_bp = int(reward_bp * ratio / 100)

    # TX BLURT
    try:
        acc.transfer(INVESTOR, investor_bp, 'BLURT', 'Thank You')
    except Exception as err:
        print('INV_TX_ERROR', err)
    finally:
        tx_data = {
            'date': today,
            'reward_bp': reward_bp,
            'investor_bp': investor_bp,
            'investor': INVESTOR,
        }
        db_prd.child(db_name).push(tx_data)


def get_budget(budget):
    reserve_name = os.environ.get('RESERVE_NAME')
    reserve_key = os.environ.get('RESERVE_KEY')
    upvote_account = os.environ.get('UPVOTE_ACCOUNT')

    blurt_obj = Blurt(get_node(), keys=[reserve_key])
    account_obj = Account(reserve_name, blockchain_instance=blurt_obj)

    # TX BLURT
    try:
        account_obj.transfer(upvote_account, budget, 'BLURT', 'Reward Budget')
    except Exception as err:
        print('GET_BUDGET_ERROR', err)


def get_reward_budget():
    budget_bp = 0
    # Get 1 day curation reward in BP
    reward_bp = account.get_curation_reward(days=1)
    # inv_tx(reward_bp)

    budget_bp = int(reward_bp * PERCENT / 100)
    get_budget(budget_bp)

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


def get_coal_list():
    coal_list = []
    db_name = 'coal_list'
    coal_data = db_prd.child(db_name).get()

    for coal in coal_data:
        coal_list.append(coal.val()['username'])

    return coal_list


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
    reward_min = REWARD_MINIMUM
    rewards = dict()
    total_bp = sum(delegations.values())

    # top_members = get_top_leaderboard()
    coal_list = get_coal_list()

    # Rewards get divided by delegation %
    for key in delegations:
        if key == INVESTOR:
            continue

        if key in coal_list:
            continue

        # Base amount
        amount = (delegations[key] / total_bp) * budget

        if amount < reward_min:
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
    b = Blurt(get_node(), keys=[active_key])
    a = Account(username, blockchain_instance=b)

    db_name = 'failed_transfer'
    today = datetime.now().strftime("%Y-%m-%d")

    # Transfer rewards to users
    for key in rewards:
        amount = f'{rewards[key]:.2f}'
        memo = f"""Hi @{key}
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
    post_key = os.environ.get('BL_POST_KEY')
    blurt_obj = Blurt(get_node(), keys=[post_key])

    today = datetime.now().strftime("%Y-%m-%d")
    title = f'Daily Delegation Payout - {today}'
    tags = ['blurtblock', 'delegation', 'rewards', 'blurt']
    # leaderboard = 'https://blurtblock.herokuapp.com/blurt/leaderboard'
    delegate_url = 'https://blurtblock.herokuapp.com/blurt/delegate'

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
<center>
[![](https://i.imgur.com/AmarQ5N.png)](https://tinyurl.com/twitter-tomoyan)
</center>
## Everyday is a BLURT day if you [delegate your BP]({delegate_url})

## Blurt Together
![](https://images.ecency.com/DQmb2VCRNTwqEBLnQp8USHpK9bZGvkBa9ynxyGtNi27vTM1/bt.gif)

This is my manual curation program.
https://blurt.blog/blurttogether/@tomoyan/blurt-together-6-6-2022

Just leave me a comment with a **favorite post** which is **NOT yours**.
It can be your friend, family or some post that you liked and deserves some love.
I will pick one comment and **manually** curate both the post and the comment.
(by me and [curation trail](https://blurtblock.herokuapp.com/blurt/trail/))

## Curation trail updated
* Auto reward claim has been added to trail followers
* Insufficient fund check has been added
(accounts that don't have enough BLURT will be removed from the trail)

## Upvote tool updated
* COAL (do not vote) list has been added
* Powering down account will not be upvoted
* Trail follow is mandatory to use free upvote

Blurt transaction fee has been increased.
If your daily reward is less than 0.1 BLURT,
you will not receive reward due to the transaction fee.
(increase BP delegation and receive more reward)
---

**Star Bonus**: You will receive stars for using upvote.
5 Stars - guarantee 100%
2.5 Starts - 25% + regular vote%
![](https://i.imgur.com/IHZYaWx.png)
The more you use, the more you earn!
https://blurtblock.herokuapp.com

Delegation Bonus 👇
If you delegate your BP to @tomoyan, you will receive daily rewards.
Also, delegators will get a **BONUS** upvote.
Just use [**Free UPVOTE**](https://blurtblock.herokuapp.com/blurt/upvote/).
https://blurtblock.herokuapp.com/blurt/upvote
Give it a try! Anybody can use it even if you don't delegate.

## Daily Rewards Today
{table}

## How to delegate BLURT POWER(BP)? Here 👇
[Delegate BP](https://blurtblock.herokuapp.com/blurt/delegate/)

Thank you for your support!
Have a Blurt Day 🙂
<center>

**BLURT for You**
![qrcode_blurtblock.herokuapp.com.png](https://i.imgur.com/Z2AXZle.png)

</center>

    """

    print('Posting')
    blurt_obj.post(
        author=username,
        title=title,
        body=body,
        tags=tags,
        self_vote=False)


if __name__ == '__main__':
    main()
