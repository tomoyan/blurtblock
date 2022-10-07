import os
import collections
from datetime import datetime, timedelta
import random
import requests

from beem import Steem
from beem.account import Account
from beem.instance import set_shared_blockchain_instance
from beem.community import Community

MINIMUM_REWARD = 0.001
COMMUNITY_NAME = os.environ.get('COMMUNITY_NAME')
COMMUNITY_ACTIVE_KEY = os.environ.get('COMMUNITY_ACTIVE_KEY')

# Setup Steem nodes
STEEMIT_NODES = [
    # 'https://steem.moonjp.xyz',
    'https://api.steem.fans',
    'https://api.steemit.com',
    'https://cn.steems.top',
    'https://steem.61bts.com'
]
random.shuffle(STEEMIT_NODES)
STEEM = Steem(node=STEEMIT_NODES, keys=[COMMUNITY_ACTIVE_KEY])
set_shared_blockchain_instance(STEEM)


def get_curation_reward():
    # Get curation reward for the last 24H
    # 50% of the reward will be divided
    # and distributed delegators
    print('GET_CURATION_REWARD')
    curation_reward = 0.0
    now = datetime.now()
    start_epoch = now - timedelta(days=1)
    start_epoch = int(start_epoch.timestamp())
    # print(f'{start_epoch=}')

    end_epoch = now
    end_epoch = int(end_epoch.timestamp())
    # print(f'{end_epoch=}')

    url = (
        'https://sds.steemworld.org'
        '/rewards_api'
        '/getRewardsSums'
        '/curation_reward'
        f'/{COMMUNITY_NAME}'
        f'/{start_epoch}-{end_epoch}'
    )
    response = requests.get(url)

    if response:
        json_data = response.json()
        vests = json_data['result']['vests']
        curation_reward = STEEM.vests_to_sp(vests)
    else:
        print('REWARDS_API_ERROR')

    curation_reward /= 2
    return curation_reward


def get_delegators():
    # Get sp delegators to jp community
    print('GET_DELEGATORS')
    delegators = []

    # Get a list of SP delegators from justyy API
    url = (
        'https://uploadbeta.com/api/steemit/delegators/?'
        'cached&'
        'id=japansteemit&'
        'hash=tomoyajapnesekasjdfahjjkhh23k3k4'
    )
    response = requests.get(url)

    if response:
        delegators = response.json()
    else:
        print('DELEGATIONS_API_ERROR')

    return delegators


def get_muted_members():
    # Get members who are muted in jp community
    print('GET_MUTED_MEMBERS')
    muted_members = []
    steem_japan = 'hive-161179'
    community = Community(steem_japan, blockchain_instance=STEEM)

    # Get a list of community roles
    roles = community.get_community_roles()

    # Find muted members
    for role in roles:
        if role[1] == 'muted':
            muted_members.append(role[0])

    return muted_members


def get_witness_voters(witness_name):
    # Get voter list of witness_name
    print('GET_WITNESS_VOTERS', witness_name)
    voters = []

    url = (
        'https://sds.steemworld.org'
        '/witnesses_api'
        '/getWitnessVotesByWitness'
        f'/{witness_name}'
    )
    response = requests.get(url)

    if response:
        json_data = response.json()
        voters = json_data['result']
        print(f'{voters=}')
    else:
        print('WITNESSES_API_ERROR')

    return voters


def process_payout(curation_reward, delegators):
    print('PROCESS_PAYOUT')

    if not curation_reward or not delegators:
        print(f'NO {curation_reward=}') if not curation_reward else print()
        print(f'NO {delegators=}') if not delegators else print()
        return

    now = datetime.now()
    today = now.strftime("%Y-%m-%d")

    tomoyan_voters = get_witness_voters('tomoyan.witness')
    yasu_voters = get_witness_voters('yasu.witness')

    ACCOUNT = Account(COMMUNITY_NAME, blockchain_instance=STEEM)

    muted_members = get_muted_members()
    # print(f'{muted_members=}')

    counter = collections.Counter()
    for d in delegators:
        counter.update(d)

    result = dict(counter)
    total_sp_delegation = result['sp']
    # print(f'{total_sp_delegation=}')

    for delegator in delegators:
        # skip muted_members
        if delegator['delegator'] in muted_members:
            print(f"MUTED: {delegator['delegator']}")
            continue

        # check witness support for tomoyan + yasu
        # and update multiplier
        multiplier = 0.5
        if delegator['delegator'] in tomoyan_voters:
            multiplier += 0.5

        if delegator['delegator'] in yasu_voters:
            multiplier += 0.5

        percentage = delegator['sp'] / total_sp_delegation
        reward = curation_reward * percentage
        reward *= multiplier

        if reward < MINIMUM_REWARD:
            print(f"MINIMUM_REWARD>{reward=} {delegator['delegator']=}")
            continue

        # Today's reward
        memo = f"""
        {today} JapanSteemit SP Delegation Reward
        - Witness 2人に投票すると報酬が50%アップ！
        Vote for @tomoyan.witness and @yasu.witness
        Daily Reward 50% UP!
        [Multiplier: {multiplier}%]
        https://steemitwallet.com/~witnesses
        """
        try:
            print(f"{delegator['delegator']=} {reward=} {memo}")
            ACCOUNT.transfer(delegator['delegator'], reward, 'STEEM', memo)
        except Exception as err:
            print(f'TRANSFER_ERROR: {err}')


def main():
    print('START_MAIN')

    curation_reward = get_curation_reward()
    # print(f'{curation_reward=}')

    delegators = get_delegators()
    # print(f'{delegators=}')

    process_payout(curation_reward, delegators)

    print('END_MAIN')


if __name__ == '__main__':
    main()
