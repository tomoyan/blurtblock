from beem.instance import set_shared_blockchain_instance
from beem.account import Account
from beem.amount import Amount
from beem.witness import Witness
from beem import Blurt

from datetime import datetime, timedelta
from statistics import mean
import random
from functools import lru_cache
# import logging
# from dumper import dump


class BlurtChain:
    """docstring for Chain"""
    # Setup node list for Blurt
    # Create Blurt chain object

    def __init__(self, username):
        self.username = username
        self.account = None
        self.witness = 0
        self.nodes = [
            # 'https://api.blurt.blog',
            # 'https://api.blurt.tools',
            # 'https://api.blurtworld.com',
            'https://rpc.blurtworld.com',
            'https://rpc.blurt.buzz',
            'https://rpc.blurt.world',
            'https://blurtd.privex.io'
        ]
        random.shuffle(self.nodes)

        self.blurt = Blurt(node=self.nodes)
        self.blockchain = set_shared_blockchain_instance(self.blurt)

        # Create account object
        try:
            self.account = Account(self.username, full=False, lazy=False)
        except Exception as e:
            self.username = None
            self.account = None
            print(f'AccountDoesNotExistsException : {e}')

        # Witness check
        try:
            Witness(self.username)
            self.witness = 1
        except Exception:
            self.witness = 0
            # print(f'WitnessDoesNotExistsException : {e}')

    @lru_cache(maxsize=32)
    def get_account_info(self):
        self.account_info = {}

        if self.username:
            # GET BLURT AMOUNT
            available_balances = self.account.available_balances
            blurt = available_balances[0]
            blurt = str(blurt).split()[0]
            self.account_info['blurt'] = f'{float(blurt):,.3f}'

            # GET BLURT POWER
            blurt_power = self.account.get_steem_power()
            self.account_info['bp'] = f'{blurt_power:,.3f}'

            # GET VOTING POWER %
            voting_power = self.account.get_voting_power()
            self.account_info['voting_power'] = f'{voting_power:.2f}'

            manabar = self.account.get_manabar()
            recharge_time = self.account.get_manabar_recharge_time_str(manabar)
            self.account_info['recharge_time_str'] = recharge_time

        return self.account_info

    @lru_cache(maxsize=32)
    def get_follower(self):
        self.follower_data = {}
        follower = []
        following = []
        common = []

        if self.username:
            follower = self.account.get_followers(self.username)
            following = self.account.get_following(self.username)
            common = set(follower) & set(following)

        for username in follower:
            if username in common:
                self.follower_data[username] = 1
            else:
                self.follower_data[username] = 0

        return self.follower_data

    @lru_cache(maxsize=32)
    def get_following(self):
        self.following_data = {}
        follower = []
        following = []
        common = []

        if self.username:
            follower = self.account.get_followers(self.username)
            following = self.account.get_following(self.username)
            common = set(follower) & set(following)

        for username in following:
            if username in common:
                self.following_data[username] = 1
            else:
                self.following_data[username] = 0

        return self.following_data

    @lru_cache(maxsize=32)
    def get_vote_history(self):
        votes = {}
        result = {}
        labels = []
        permlinks = []
        count_data = []
        weight_data = []
        total_votes = 0
        stop = datetime.utcnow() - timedelta(days=7)

        if self.username:
            history = self.account.history_reverse(
                stop=stop, only_ops=['vote'])

            # Count how many times voted in 7 days
            for data in history:
                if self.username == data["voter"]:
                    permlink = f'@{data["author"]}/{data["permlink"]}'
                    permlinks.append(permlink)

                    if data["author"] in votes.keys():
                        votes[data["author"]]['count'] += 1
                        votes[data["author"]
                              ]['weight'].append(data["weight"])
                    else:
                        votes[data["author"]] = {
                            'count': 1,
                            'weight': [data["weight"]],
                        }
                else:
                    next

            for key, value in votes.items():
                labels.append(key)
                count_data.append(value['count'])
                weight_data.append(mean(value['weight']) * 0.01)

                total_votes += value['count']
                value['weight'] = mean(value['weight']) * 0.01

        result['total_votes'] = total_votes

        result['labels'] = labels
        result['permlinks'] = sorted(permlinks)
        result['count_data'] = count_data
        result['weight_data'] = weight_data

        return result

    @lru_cache(maxsize=32)
    def get_mute(self):
        data = {}

        if self.username:
            data['muter'] = self.account.get_muters()
            data['muting'] = self.account.get_mutings()

        return data

    @lru_cache(maxsize=32)
    def get_delegation(self):
        # find delegations for username
        data = {}

        if self.username:
            # find outgoing delegatons
            data['outgoing'] = self.account.get_vesting_delegations()
            for value in data['outgoing']:
                value['bp'] = self.vests_to_bp(value['vesting_shares'])

            # find expiring delegatons
            data['expiring'] = self.account.get_expiring_vesting_delegations()
            for value in data['expiring']:
                value['bp'] = self.vests_to_bp(value['vesting_shares'])
                date_time = value['expiration'].split('T')
                value['expiration'] = f'{date_time[0]} {date_time[-1]}'

            # find incoming delegatons
            data['incoming'] = []
            # incoming_temp = dict()
            # blurt_start_time = datetime(2020, 7, 1)

            # delegate_vesting_shares = self.account.history(
            #     only_ops=["delegate_vesting_shares"], batch_size=1000)

            # for operation in delegate_vesting_shares:
            #     timestamp = datetime.strptime(
            #         operation['timestamp'], "%Y-%m-%dT%H:%M:%S")

            #     if timestamp < blurt_start_time:
            #         continue

            #     if self.username == operation["delegator"]:
            #         continue

            #     if operation["vesting_shares"] == '0.000000 VESTS':
            #         incoming_temp.pop(operation["delegator"])
            #         continue
            #     else:
            #         incoming_temp[operation["delegator"]] = operation

            # if incoming_temp:
            #     for key, value in incoming_temp.items():
            #         value['bp'] = self.vests_to_bp(value['vesting_shares'])
            #         data['incoming'].append(value)

        return data

    def vests_to_bp(self, vests):
        # VESTS to BP conversion
        bp = 0.000
        v = Amount(vests)
        bp = self.blurt.vests_to_bp(v.amount)
        bp = f'{bp:.3f}'

        return bp

    @lru_cache(maxsize=32)
    def get_reward_summary(self):
        # find reward summary for username
        data = {
            'author_day': f'{0.0:.3f}',
            'author_week': f'{0.0:.3f}',
            # 'author_month': f'{0.0:.3f}',
            'curation_day': f'{0.0:.3f}',
            'curation_week': f'{0.0:.3f}',
            # 'curation_month': f'{0.0:.3f}',
            'producer_day': f'{0.0:.3f}',
            'producer_week': f'{0.0:.3f}',
            # 'producer_month': f'{0.0:.3f}',
        }

        if self.username:
            day = datetime.utcnow() - timedelta(days=1)
            week = datetime.utcnow() - timedelta(days=7)
            # month = datetime.utcnow() - timedelta(days=30)

            # get account history
            ops = ['author_reward', 'curation_reward', 'producer_reward']
            day_history = self.account.history_reverse(
                stop=day, only_ops=ops)

            week_history = self.account.history_reverse(
                stop=week, only_ops=ops)

            # month_history = self.account.history_reverse(
            #     stop=month, only_ops=ops)

            # 1 day rewards
            day_rewards = self.rewards(day_history)
            data['author_day'] = day_rewards['author']
            data['curation_day'] = day_rewards['curation']
            data['producer_day'] = day_rewards['producer']

            # 7 day rewards
            week_rewards = self.rewards(week_history)
            data['author_week'] = week_rewards['author']
            data['curation_week'] = week_rewards['curation']
            data['producer_week'] = week_rewards['producer']

            # 30 day rewards
            # month_rewards = self.rewards(month_history)
            # data['author_month'] = month_rewards['author']
            # data['curation_month'] = month_rewards['curation']
            # data['producer_month'] = month_rewards['producer']

        return data

    @lru_cache(maxsize=32)
    def rewards(self, history):
        data = {}
        author_bp = 0.0
        curation_bp = 0.0
        producer_bp = 0.0

        author_reward_vests = Amount("0 VESTS")
        curation_reward_vests = Amount("0 VESTS")
        producer_reward_vests = Amount("0 VESTS")

        for reward in history:
            if reward['type'] == 'author_reward':
                author_reward_vests += Amount(reward['vesting_payout'])

            if reward['type'] == 'curation_reward':
                curation_reward_vests += Amount(reward['reward'])

            if self.witness:
                if reward['type'] == 'producer_reward':
                    producer_reward_vests += Amount(reward['vesting_shares'])

        author_bp = self.blurt.vests_to_bp(author_reward_vests.amount)
        curation_bp = self.blurt.vests_to_bp(curation_reward_vests.amount)
        producer_bp = self.blurt.vests_to_bp(producer_reward_vests.amount)

        author_bp = f'{author_bp:.3f}'
        curation_bp = f'{curation_bp:.3f}'
        producer_bp = f'{producer_bp:.3f}'

        data = {
            'author': author_bp,
            'curation': curation_bp,
            'producer': producer_bp,
        }

        return data
