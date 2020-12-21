from beem.instance import set_shared_blockchain_instance
from beem.account import Account
from beem.amount import Amount
from beem.witness import Witness
from beem import Blurt
from config import Config

from datetime import datetime, timedelta
from statistics import mean
from functools import lru_cache
import random
# import ast
import requests
import pyrebase

# Firebase configuration
serviceAccountCredentials = {
    "type": "service_account",
    "project_id": "blurtdb",
    "private_key_id": Config.FB_PRIVATE_KEY_ID,
    "private_key": Config.FB_PRIVATE_KEY,
    "client_email": Config.FB_CLIENT_EMAIL,
    "client_id": Config.FB_CLIENT_ID,
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": Config.FB_AUTH_PROVIDER_X509_CERT_URL,
    "client_x509_cert_url": Config.FB_CLIENT_X509_CERT_URL
}
firebase_config = {
    "apiKey": Config.FB_APIKEY,
    "authDomain": Config.FB_AUTHDOMAIN,
    "databaseURL": Config.FB_DATABASEURL,
    "storageBucket": Config.FB_STORAGEBUCKET,
    # "serviceAccount": serviceAccountCredentials,
}
# Firebase initialization
firebase = pyrebase.initialize_app(firebase_config)


class BlurtChain:
    """docstring for Chain"""
    # Setup node list for Blurt
    # Create Blurt chain object

    def __init__(self, username):
        self.username = username
        self.account = None
        self.witness = 0
        self.nodes = [
            'https://rpc.blurt.buzz',
            # 'https://blurtd.privex.io',
            # 'https://rpc.blurtworld.com',
            # 'https://rpc.blurt.world',
            # 'https://api.softmetal.xyz',
        ]
        random.shuffle(self.nodes)

        self.blurt = Blurt(node=self.nodes)
        self.blockchain = set_shared_blockchain_instance(self.blurt)

        # Get a reference to the database service
        self.firebase = firebase.database()

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

    @lru_cache(maxsize=128)
    def get_vote_history(self, username):
        votes = {}
        result = {}
        labels = []
        permlinks = []
        upvotes = []
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
                    timestamp = datetime.strptime(
                        data['timestamp'], '%Y-%m-%dT%H:%M:%S')
                    permlink = f'@{data["author"]}/{data["permlink"]}'
                    weight = data['weight'] * 0.01
                    link_data = {
                        'timestamp': timestamp,
                        'permlink': permlink,
                        'weight': weight,
                    }
                    permlinks.append(link_data)

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
                    timestamp = datetime.strptime(
                        data['timestamp'], '%Y-%m-%dT%H:%M:%S')
                    voter = data['voter']
                    permlink = f'@{data["author"]}/{data["permlink"]}'
                    weight = data['weight'] * 0.01
                    upvote_data = {
                        'timestamp': timestamp,
                        'voter': voter,
                        'permlink': permlink,
                        'weight': weight,
                    }
                    upvotes.append(upvote_data)

            for key, value in votes.items():
                labels.append(key)
                count_data.append(value['count'])
                weight_data.append(mean(value['weight']) * 0.01)

                total_votes += value['count']
                value['weight'] = mean(value['weight']) * 0.01

        result['total_votes'] = total_votes

        result['labels'] = labels
        result['permlinks'] = permlinks
        result['upvotes'] = upvotes
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
    def get_delegation_new(self, option):
        # find delegation for username
        data = {}

        if not self.username:
            return data

        # find incoming delegaton
        if option == "in":
            data['incoming'] = []
            incoming_temp = dict()
            blurt_start_time = datetime(2020, 7, 1)

            delegate_vesting_shares = self.account.history(
                only_ops=["delegate_vesting_shares"], batch_size=10000)

            for operation in delegate_vesting_shares:
                timestamp = datetime.strptime(
                    operation['timestamp'], "%Y-%m-%dT%H:%M:%S")

                if timestamp < blurt_start_time:
                    continue

                if self.username == operation["delegator"]:
                    continue

                if operation["vesting_shares"] == '0.000000 VESTS':
                    incoming_temp.pop(operation["delegator"])
                    continue
                else:
                    incoming_temp[operation["delegator"]] = operation

            if incoming_temp:
                for key, value in incoming_temp.items():
                    value['bp'] = self.vests_to_bp(value['vesting_shares'])
                    data['incoming'].append(value)
        # find outgoing delegaton
        elif option == "out":
            data['outgoing'] = self.account.get_vesting_delegations()
            for value in data['outgoing']:
                value['bp'] = self.vests_to_bp(value['vesting_shares'])
        # find expiring delegaton
        elif option == "exp":
            data['expiring'] = self.account.get_expiring_vesting_delegations()
            for value in data['expiring']:
                value['bp'] = self.vests_to_bp(value['vesting_shares'])
                date_time = value['expiration'].split('T')
                value['expiration'] = f'{date_time[0]} {date_time[-1]}'
        else:
            return data

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
            incoming_temp = dict()
            blurt_start_time = datetime(2020, 7, 1)

            delegate_vesting_shares = self.account.history(
                only_ops=["delegate_vesting_shares"], batch_size=10000)

            for operation in delegate_vesting_shares:
                timestamp = datetime.strptime(
                    operation['timestamp'], "%Y-%m-%dT%H:%M:%S")

                if timestamp < blurt_start_time:
                    continue

                if self.username == operation["delegator"]:
                    continue

                if operation["vesting_shares"] == '0.000000 VESTS':
                    incoming_temp.pop(operation["delegator"])
                    continue
                else:
                    incoming_temp[operation["delegator"]] = operation

            if incoming_temp:
                for key, value in incoming_temp.items():
                    value['bp'] = self.vests_to_bp(value['vesting_shares'])
                    data['incoming'].append(value)

        return data

    def vests_to_bp(self, vests):
        # VESTS to BP conversion
        bp = 0.000
        v = Amount(vests)
        bp = self.blurt.vests_to_bp(v.amount)
        bp = f'{bp:.3f}'

        return bp

    @lru_cache(maxsize=32)
    def get_author_reward(self, duration):
        if duration < 1 or duration > 30:
            duration = 1
        author_reward = f"{0.0:.3f}"

        if self.username:
            stop = datetime.utcnow() - timedelta(days=duration)

            # get author_reward history
            reward_history = self.account.history_reverse(
                stop=stop, only_ops=['author_reward'])

            # convert reward vest to blurt power
            reward = self.rewards(reward_history)
            author_reward = f"{float(reward['author']):.3f}"

        return author_reward

    @lru_cache(maxsize=32)
    def get_curation_reward(self, duration):
        if duration < 1 or duration > 30:
            duration = 1
        curation_reward = f"{0.0:.3f}"
        curation_reward = self.account.get_curation_reward(days=duration)

        return f"{curation_reward:.3f}"

    @lru_cache(maxsize=32)
    def get_producer_reward(self, duration):
        if duration < 1 or duration > 30:
            duration = 1
        producer_reward = f"{0.0:.3f}"

        if self.username and self.witness:
            stop = datetime.utcnow() - timedelta(days=duration)

            # get author_reward history
            reward_history = self.account.history_reverse(
                stop=stop, only_ops=['producer_reward'])

            # convert reward vest to blurt power
            reward = self.rewards(reward_history)
            producer_reward = f"{float(reward['producer']):.3f}"

        return producer_reward

    @lru_cache(maxsize=32)
    def get_reward_summary(self, duration, **kwargs):
        data = {
            'author': f'{0.0:.3f}',
            'curation': f'{0.0:.3f}',
            'producer': f'{0.0:.3f}',
            'total': f'{0.0:.3f}',
        }
        # option = kwargs.get('option', None)

        if self.username:
            if duration < 1 or duration > 30:
                duration = 1

            # get account history
            ops = ['author_reward', 'curation_reward', 'producer_reward']
            reward_history = {}

            stop = datetime.utcnow() - timedelta(days=duration)
            reward_history = self.account.history_reverse(
                stop=stop, only_ops=ops)

            # convert reward vest to blurt power
            rewards = self.rewards(reward_history)

            # rewards total
            data['total'] = float(rewards['author']) + \
                float(rewards['curation']) + \
                float(rewards['producer'])
            data['total'] = f"{data['total']:,.3f}"
            data['author'] = f"{float(rewards['author']):,.3f}"
            data['curation'] = f"{float(rewards['curation']):,.3f}"
            data['producer'] = f"{float(rewards['producer']):,.3f}"

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

    def process_data(self, count_type, data):
        result = 0

        if count_type in data:
            result = data[count_type]

        return result

    @lru_cache(maxsize=32)
    def get_stats(self):
        stats_data = {}
        labels = []

        # get counts of each operation
        ops = [
            'labels', 'total', 'vote',
            'comment', 'account_create',
            'transfer_to_vesting',
            'withdraw_vesting',
        ]

        for op in ops:
            stats_data[op] = []

        # get stats data from firebase
        db_name = "blurt_stats"
        fb_stats_data = self.firebase.child(
            db_name).order_by_key().limit_to_last(1).get()

        fb_stats = {}
        for data in fb_stats_data.each():
            fb_stats = data.val()

        # only use last 6 months stats
        months = list(fb_stats.keys())[-6:]

        for stats in fb_stats:
            if stats in months:
                labels.append(stats)

            for op in ops:
                stats_data[op].append(
                    self.process_data(op, fb_stats[stats]))

        stats_data['labels'] = labels

        return stats_data

    def check_witness(self, username):
        witness_list = []
        result = {
            'status': False,
            'message': 'Error: Post URL'
        }

        endpoint = self.nodes[0]
        post_data = {
            'id': '0',
            'jsonrpc': '2.0',
            'method': 'call',
            'params': ['condenser_api', 'get_accounts', [[username]]]
        }

        try:
            response = requests.post(endpoint, json=post_data, timeout=3)

            # If the response was successful,
            # no Exception will be raised
            response.raise_for_status()
        except Exception as err:
            # print(f'Error has occurred: {err}')
            result['message'] = f'Error has occurred: {err}'
            return result

        if response:
            json_response = response.json()
            if json_response['result']:
                witness_list = json_response['result'][0]['witness_votes']
            else:
                return result

        if 'tomoyan' in witness_list:
            result['status'] = True
            result['message'] = 'Thank you for your support.'
        else:
            result['message'] = 'Error: Please vote for my witness ☝️'

        return result

    def check_last_upvote(self, username):
        # 24 hour = 86400 sec
        # 12 hour = 43200 sec
        wait_time = 43200.0
        result = False

        # get the last upvote record
        record = self.firebase.child("upvote_log").order_by_child(
            "username").equal_to(username).limit_to_last(1).get()

        if not record.val():
            result = True
            return result

        # check if last upvoted is more than wait_time
        for data in record.each():
            val = data.val()

            current_time = datetime.now()
            last_vote = val['created']
            last_vote = datetime.strptime(last_vote, "%m/%d/%Y %H:%M:%S")

            time_diff = current_time - last_vote

            if time_diff.total_seconds() >= wait_time:
                result = True

        return result

    def delegation_bonus(self, username):
        bonus_weight = 0.0

        blurt = Blurt(node=self.nodes)
        account = Account(username, blockchain_instance=blurt)

        # check delegation_bonus (bonus_weight 0 - 30%)
        vesting_delegations = account.get_vesting_delegations()
        for delegation in vesting_delegations:
            if delegation["delegatee"] == "tomoyan":
                vesting_shares = Amount(delegation["vesting_shares"])
                delegation_bp = self.blurt.vests_to_bp(vesting_shares.amount)

                if delegation_bp > 0.0 and delegation_bp <= 1000.0:
                    bonus_weight = round(random.uniform(0, 5), 2)
                elif delegation_bp > 1000.0 and delegation_bp <= 10000.0:
                    bonus_weight = round(random.uniform(5, 10), 2)
                elif delegation_bp > 10000.0 and delegation_bp <= 100000.0:
                    bonus_weight = round(random.uniform(10, 20), 2)
                elif delegation_bp > 100000.0 and delegation_bp <= 1000000.0:
                    bonus_weight = round(random.uniform(20, 30), 2)
                elif delegation_bp > 1000000.0:
                    bonus_weight = 30.0

                break

        return bonus_weight

    def upvote_post(self, identifier, bonus_weight):
        upvote_account = Config.UPVOTE_ACCOUNT
        upvote_key = Config.UPVOTE_KEY

        vote_result = {
            "status": False,
            "message": "Error"
        }

        blurt = Blurt(node=self.nodes, keys=[upvote_key])
        account = Account(upvote_account, blockchain_instance=blurt)

        # random vote_weight (40-70 %)
        vote_weight = round(random.uniform(40, 70), 2)

        # add delegation_bonus (bonus_weight 0 - 30%)
        vote_weight += bonus_weight
        if vote_weight > 100.0:
            vote_weight = 100.0

        try:
            result = blurt.vote(vote_weight, identifier, account=account)
            vote_result["status"] = True
            vote_result["message"] = f"Upvoted: {result}"
        except Exception as err:
            print(err)
            vote_result["message"] = f"Error: Please check your URL {err}"

        return vote_result

    def check_active_post(self, post_str):
        active_posts = []
        cashout_time = "1969-12-31T23:59:59"
        result = False

        strings = post_str.split('/')
        username = strings[0]
        post_id = strings[1]
        blurt = Blurt(node=self.nodes)
        blurt_account = Account(username, blockchain_instance=blurt)
        posts = blurt_account.get_blog(raw_data=True)

        for post in posts:
            # post has been paid out
            if post["comment"]["cashout_time"] == cashout_time:
                continue

            if post["blog"]:
                active_posts.append(post["comment"]["permlink"])

        if post_id in active_posts:
            result = True

        return result

    def coal_check(self, username):
        result = {
            'status': False,
            'message': 'Error: Sorry user is listed in COAL'
        }

        endpoint = "https://api.blurt.buzz/blacklist"

        get_result = self.get_request(endpoint)
        response = get_result["response"]

        if response:
            json_response = response.json()
            for res in json_response:
                if res["name"] == username:
                    # username is listed in coal
                    return result

            result = {
                'status': True,
                'message': 'OK'
            }

        return result

    def save_data_fb(self, db_name, data):
        # save data into firebase database
        result = self.firebase.child(db_name).push(data)
        return result

    def process_upvote(self, url):
        username = None
        identifier = None
        now = datetime.now()
        current_time = now.strftime("%m/%d/%Y %H:%M:%S")

        data = {
            'status': False,
            'message': 'Error: Post URL'
        }

        # save access_data
        access_data = {
            'url': url,
            'created': current_time,
        }
        self.save_data_fb("access_log", access_data)

        # check post url check
        strings = url.split("@")

        if len(strings) != 2:
            return data

        identifier = f'@{strings[1]}'
        username = strings[1].split('/')[0]
        if not username:
            return data

        # check last upvote
        can_vote = self.check_last_upvote(username)
        if can_vote is False:
            data['message'] = 'Error: Please come back later (every 12h)'
            return data

        # check witness (using condenser_api)
        witness_data = self.check_witness(username)
        if witness_data['status'] is False:
            data['message'] = witness_data['message']
            return data

        # check post is active
        active_post = self.check_active_post(strings[1])
        if active_post is False:
            data['message'] = 'Error: This post is too old to upvote'
            return data

        # coal user check
        is_coal = self.coal_check(username)
        if is_coal["status"] is False:
            data['message'] = is_coal["message"]
            return data

        # check delegation bonus
        bonus_weight = self.delegation_bonus(username)

        # upvote
        is_upvoted = self.upvote_post(identifier, bonus_weight)
        if is_upvoted["status"] is False:
            data['message'] = is_upvoted["message"]
            return data

        # save upvote_data
        upvote_data = {
            'username': username,
            'identifier': identifier,
            'created': current_time,
            'bonus_weight': bonus_weight,
        }
        self.save_data_fb("upvote_log", upvote_data)

        data = {
            'status': True,
            'message': 'Thank You. Your post has been upvoted.'
        }

        return data

    def get_request(self, endpoint, **kwargs):
        """
        endpoint = "https://httpbin.org/get"
        params = {'page': 2, 'count': 3}
        result = self.get_request(endpoint, **params)
        """

        result = {
            'status': False,
            'message': 'Error'
        }

        try:
            response = requests.get(endpoint, params=kwargs, timeout=3)
            response.raise_for_status()
        except Exception as err:
            result['message'] = f'Error has occurred: {err}'
            return result

        if response:
            result['status'] = True
            result['message'] = 'OK'
            result['response'] = response

        return result

    def post_request(self, endpoint, **kwargs):
        result = {
            'status': False,
            'message': 'Error'
        }

        return result
