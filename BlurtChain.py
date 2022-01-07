from beem.instance import set_shared_blockchain_instance
from beem.account import Account
from beem.amount import Amount
from beem.comment import Comment
# from beem.witness import Witness
from beemapi.noderpc import NodeRPC
from beem import Blurt
from config import Config
from beemgraphenebase.account import PrivateKey

from flask import Markup
from datetime import datetime, timedelta
from functools import lru_cache
import random
import requests
import pyrebase
import base64
import json
from markdown import markdown
from operator import itemgetter
import concurrent.futures
import cryptocode

# Firebase configuration
serviceAccountCredentials = json.loads(
    base64.b64decode(Config.FB_SERVICEACCOUNT.encode()).decode())
firebase_config = {
    "apiKey": Config.FB_APIKEY,
    "authDomain": Config.FB_AUTHDOMAIN,
    "databaseURL": Config.FB_DATABASEURL,
    "storageBucket": Config.FB_STORAGEBUCKET,
    "serviceAccount": serviceAccountCredentials,
}
# Firebase initialization
firebase = pyrebase.initialize_app(firebase_config)

BLURT_NODES = [
    'https://rpc.blurt.world',
    'https://blurt-rpc.saboin.com',
    'https://rpc.tekraze.com',
    # 'https://rpc.dotwin1981.de',
    'https://rpc.nerdtopia.de',
    'https://kentzz.blurt.world',
    'https://rpc.blurtlatam.com',
    # 'https://blurt.ecosynthesizer.com',
]
random.shuffle(BLURT_NODES)


class BlurtChain:
    """docstring for Chain"""
    # Setup node list for Blurt
    # Create Blurt chain object

    def __init__(self, username):
        self.username = username
        self.account = None
        self.witness = 0
        self.nodes = BLURT_NODES

        self.blurt = Blurt(node=self.nodes, num_retries=10)
        self.blockchain = set_shared_blockchain_instance(self.blurt)

        # Get a reference to the database service
        self.firebase = firebase.database()

        # Create account object
        try:
            self.account = Account(self.username, full=False, lazy=False)
        except Exception:
            self.username = None
            self.account = None

    @lru_cache(maxsize=32)
    def get_account_info(self):
        self.account_info = {}

        if self.username:
            # GET VOTING POWER %
            voting_power = self.account.get_voting_power()
            self.account_info['voting_power'] = f'{voting_power:.2f}'

            manabar = self.account.get_manabar()
            recharge_time = self.account.get_manabar_recharge_time_str(manabar)
            self.account_info['recharge_time_str'] = recharge_time

            # GET ACCOUNT DETAILS
            noderpc = NodeRPC('https://rpc.blurt.world')
            account_data = noderpc.get_account(self.username)[0]
            self.account_info['username'] = account_data['name']

            # BLURT BALANCE
            balance = float(account_data['balance'].split()[0])
            self.account_info['blurt'] = f'{balance:,.3f}'

            # BLURT POWER
            vesting_shares = account_data['vesting_shares']
            vesting_shares = float(self.vests_to_bp(vesting_shares))
            self.account_info['bp'] = f'{vesting_shares:,.3f}'

            # SAVINGS BALANCE
            savings_balance = account_data['savings_balance']
            savings_balance = float(account_data['savings_balance'].split()[0])
            self.account_info['savings'] = f'{savings_balance:,.3f}'

            # CURRENT REWARDS in BLURT and BLURT POWER
            # BLURT REWARD
            reward_blurt = float(
                account_data['reward_blurt_balance'].split()[0])
            self.account_info['reward_blurt'] = f'{reward_blurt:,.3f}'

            # BP REWARD
            reward_bp = float(
                account_data['reward_vesting_blurt'].split()[0])
            self.account_info['reward_bp'] = f'{reward_bp:,.3f}'

            # DELEGATED BP
            delegated_bp = account_data['delegated_vesting_shares']
            delegated_bp = float(self.vests_to_bp(delegated_bp))
            self.account_info['delegated_bp'] = f'{delegated_bp:,.3f}'

            # RECEIVED BP
            received_bp = account_data['received_vesting_shares']
            received_bp = float(self.vests_to_bp(received_bp))
            self.account_info['received_bp'] = f'{received_bp:,.3f}'

            # GET EFFECTIVE BLURT POWER (staked token + delegations)
            token_power = self.account.get_token_power()
            self.account_info['effective'] = f'{token_power:,.3f}'

            # POWERDOWN SCHEDULE
            withdraw_bp = account_data['vesting_withdraw_rate']
            withdraw_bp = float(self.vests_to_bp(withdraw_bp))
            self.account_info['withdraw_bp'] = f'{withdraw_bp:,.3f}'
            withdraw_date = account_data['next_vesting_withdrawal']
            withdraw_date = datetime.strptime(
                withdraw_date, '%Y-%m-%dT%H:%M:%S')

            current_date = datetime.utcnow()
            if current_date > withdraw_date:
                self.account_info['withdraw_date'] = '--'
            else:
                self.account_info['withdraw_date'] = withdraw_date

            # leaderboard rank
            ranking = self.get_ranking(self.username)
            self.account_info['ranking'] = ranking

            # get upvote count and convert into stars
            # 1 to 5 ⭐⭐⭐⭐⭐ ratings
            stars = self.get_star_rating(self.username)
            self.account_info['stars'] = stars

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
    def get_pending_posts(self):
        active_posts = []
        posts = self.account.blog_history(limit=50)

        for post in posts:
            c = Comment(post['authorperm'], blockchain_instance=self.blurt)
            time_elapsed = c.time_elapsed()

            # Skip old posts(7 days = 604800 sec)
            if time_elapsed.total_seconds() > 604800:
                break

            rewards = c.get_author_rewards()

            if rewards['pending_rewards']:
                active_posts.append({
                    'title': c['title'],
                    'authorperm': post['authorperm'],
                    'pending_rewards': rewards['total_payout'],
                })

        return active_posts

    @ lru_cache(maxsize=128)
    def get_vote_history(self, username):
        result = {}
        labels = []
        permlinks = []
        upvotes = []
        count_data = []
        weight_data = []
        total_votes = 0
        stop = datetime.utcnow() - timedelta(days=1)

        if self.username:
            history = self.account.history_reverse(
                stop=stop, only_ops=['vote'])

            # Count how many times voted in 7 days
            for data in history:
                permlink = f'@{data["author"]}/{data["permlink"]}'
                weight = f"{data['weight'] * 0.01:.2f}"
                timestamp = datetime.strptime(
                    data['timestamp'], '%Y-%m-%dT%H:%M:%S')
                if self.username == data["voter"]:
                    link_data = {
                        'timestamp': timestamp,
                        'permlink': permlink,
                        'weight': weight,
                    }
                    permlinks.append(link_data)

                else:
                    voter = data['voter']
                    upvote_data = {
                        'timestamp': timestamp,
                        'voter': voter,
                        'permlink': permlink,
                        'weight': weight,
                    }
                    upvotes.append(upvote_data)

        result['total_votes'] = total_votes

        result['labels'] = labels
        result['permlinks'] = permlinks
        result['upvotes'] = upvotes
        result['count_data'] = count_data
        result['weight_data'] = weight_data

        return result

    @ lru_cache(maxsize=32)
    def get_mute(self):
        data = {}

        if self.username:
            data['muter'] = self.account.get_muters()
            data['muting'] = self.account.get_mutings()

        return data

    def get_incoming_delegation(self, username):
        current_time = datetime.utcnow().strftime("%m/%d/%Y %H:%M:%S")
        db_name = 'incoming_delegation'
        account = Account(username, blockchain_instance=self.blurt)

        fb_key = None
        fb_data = None
        fb_block_num = 0

        # Check user data in fb
        user_record = self.firebase.child(db_name).order_by_child(
            "username").equal_to(str(username)).get().val()

        if user_record:
            record = next(iter(user_record.items()))
            fb_key = record[0]
            fb_data = record[1]
            fb_block_num = fb_data['block_num']
        else:
            save_data = {
                'username': username,
                'block_num': 0,
                'created': current_time,
            }
            save_result = self.firebase.child(db_name).push(save_data)
            fb_key = save_result['name']

        delegate_vesting_shares = account.history(
            start=fb_block_num,
            use_block_num=True,
            only_ops=["delegate_vesting_shares"])

        for op in delegate_vesting_shares:
            if op['delegator'] == username:
                continue

            amount_vests = Amount(op['vesting_shares'])
            amount = self.blurt.vests_to_bp(amount_vests)

            # replace "." sign in username with "+"
            delegator = op['delegator'].replace(".", "+")
            delegation_data = {
                'timestamp': op['timestamp'],
                'amount': amount,
            }

            # Save/Update delegation data
            if amount:
                self.firebase.child(db_name).child(fb_key).child(
                    'delegators').child(delegator).update(delegation_data)
            else:
                self.firebase.child(db_name).child(fb_key).child(
                    'delegators').child(delegator).remove()

            # Update block_num
            if op['block']:
                self.firebase.child(db_name).child(fb_key).update({
                    'block_num': op['block'],
                    'created': current_time
                })

        # Remove record if no incoming delegation
        delegation_record = self.firebase.child(db_name).child(
            fb_key).child('delegators').get().val()

        if delegation_record is None:
            self.firebase.child(db_name).child(fb_key).remove()

    @ lru_cache(maxsize=32)
    def get_delegation_new(self, option):
        # find delegation for username
        data = {}

        if not self.username:
            return data

        # find incoming delegaton
        if option == "in":
            # node_list = ['https://rpc.blurt.world']
            blurt = Blurt(BLURT_NODES)
            blurt_account = Account(self.username, blockchain_instance=blurt)

            data['incoming'] = []
            incoming_temp = dict()

            delegate_vesting_shares = blurt_account.history(
                only_ops=["delegate_vesting_shares"])

            # find delegators
            for operation in delegate_vesting_shares:
                if self.username == operation["delegator"]:
                    continue
                incoming_temp[operation["delegator"]] = operation

            for key in incoming_temp:
                info = incoming_temp[key]

                if info['vesting_shares'] == '0.000000 VESTS':
                    # skip 0 VESTS
                    continue
                else:
                    # convert VESTS to BP
                    info['bp'] = self.vests_to_bp(info['vesting_shares'])
                    info['bp'] = f"{float(info['bp']):,.3f}"
                    data['incoming'].append(info)
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

    def vests_to_bp(self, vests):
        # VESTS to BP conversion
        bp = 0.000
        v = Amount(vests)
        bp = self.blurt.vests_to_bp(v.amount)
        bp = f'{bp:.3f}'

        return bp

    def process_data(self, count_type, data):
        result = 0

        if count_type in data:
            result = data[count_type]

        return result

    def is_coal(self, username):
        # check if user is in coal_list
        # coal user won't be upvoted
        result = False
        db_name = 'coal_list'

        is_coal = self.firebase.child(
            db_name).order_by_child("username").equal_to(username).get().val()

        if len(is_coal):
            result = True

        return result

    def is_ignored(self, username):
        # check to see if user is in ignore_list
        # ignored user won't be upvoted
        result = False
        db_name = 'ignore_list'
        ignored_users = self.firebase.child(db_name).get()

        for user in ignored_users.each():
            value = user.val()
            if value['username'] == username:
                result = True
                break

        return result

    def check_last_ip(self, client_ip):
        print('CHECK_LAST_IP', client_ip)
        # 1 hour = 3600 sec
        wait_time = 3600.0
        last_vote = None
        result = False

        # get the last upvote data
        db_name = 'upvote_log'
        logs = self.firebase.child(db_name).get()

        for log in logs.each():
            value = log.val()
            if value['client_ip'] == client_ip:
                last_vote = value['created']
                print('FB DATA FOUND')
                print(value['client_ip'])
                print(value['username'])
                print(value['created'])
                print(value['vote_weight'])
                print()

        if last_vote is None:
            result = True
            return result

        # check if last voted ip is more than wait_time
        current_time = datetime.utcnow()
        last_vote = datetime.strptime(last_vote, "%m/%d/%Y %H:%M:%S")
        print('CURRENT_TIME', current_time)
        print('LAST_VOTED', last_vote)

        time_diff = current_time - last_vote

        if time_diff.total_seconds() >= wait_time:
            result = True

        return result

    def check_last_upvote(self, username):
        # 24 hour = 86400 sec
        # 20 hour = 72000 sec
        # 21 hour = 75600 sec
        wait_time = 75600.0
        result = False
        self.wait_time = None

        # get the last upvote record
        record = self.firebase.child("upvote_log").order_by_child(
            "username").equal_to(username).limit_to_last(1).get()

        if not record.val():
            result = True
            return result

        # check if last upvoted is more than wait_time
        for data in record.each():
            val = data.val()

            current_time = datetime.utcnow()
            last_vote = val['created']
            last_vote = datetime.strptime(last_vote, "%m/%d/%Y %H:%M:%S")

            time_diff = current_time - last_vote

            if time_diff.total_seconds() >= wait_time:
                result = True
            else:
                seconds = wait_time - time_diff.total_seconds()
                wait = timedelta(seconds=seconds)
                # convert wait time: WAIT_TIME 11:58:20
                self.wait_time = str(wait).split('.')[0]

        return result

    def delegation_bonus(self, username):
        bonus_weight = 0.0

        blurt = Blurt(node=self.nodes)
        account = Account(username, blockchain_instance=blurt)

        # check delegation_bonus (bonus_weight 10 - 50%)
        vesting_delegations = account.get_vesting_delegations()
        for delegation in vesting_delegations:
            if delegation["delegatee"] == "tomoyan":
                vesting_shares = Amount(delegation["vesting_shares"])
                delegation_bp = self.blurt.vests_to_bp(vesting_shares.amount)

                if 1.0 <= delegation_bp < 100.0:
                    bonus_weight = round(random.uniform(1, 5), 2)
                elif 100.0 <= delegation_bp < 500.0:
                    bonus_weight = round(random.uniform(5, 10), 2)
                elif 500.0 <= delegation_bp < 1000.0:
                    bonus_weight = round(random.uniform(10, 15), 2)
                elif 1000.0 <= delegation_bp < 3000.0:
                    bonus_weight = round(random.uniform(15, 20), 2)
                elif 3000.0 <= delegation_bp < 5000.0:
                    bonus_weight = round(random.uniform(20, 25), 2)
                elif 5000.0 <= delegation_bp < 10000.0:
                    bonus_weight = round(random.uniform(25, 30), 2)
                elif 10000.0 <= delegation_bp < 30000.0:
                    bonus_weight = round(random.uniform(30, 35), 2)
                elif 30000.0 <= delegation_bp < 50000.0:
                    bonus_weight = round(random.uniform(35, 40), 2)
                elif 50000.0 <= delegation_bp < 100000.0:
                    bonus_weight = round(random.uniform(40, 45), 2)
                elif delegation_bp >= 100000.0:
                    bonus_weight = 50.0

                break

        return bonus_weight

    def member_bonus(self, username):
        bonus_weight = 0.0
        member_list = []
        db_name = "user_level"
        level = 100

        users = self.firebase.child(db_name).child(level).get()

        for user in users.each():
            data = user.val()
            member_list.append(data["username"])

        if username in member_list:
            bonus_weight = 100.0
        else:
            # add leaderboard upvote bonus
            # check leaderboard rank
            ranking = self.get_ranking(username)
            if ranking == 1:
                bonus_weight = 20.0
            elif ranking == 2:
                bonus_weight = 10.0
            elif ranking == 3:
                bonus_weight = 5.0

        return bonus_weight

    def upvote_post(self, identifier, delegation_bonus, member_bonus):
        upvote_account = Config.UPVOTE_ACCOUNT
        upvote_key = Config.UPVOTE_KEY

        vote_result = {
            "status": False,
            "message": "Error"
        }

        blurt = Blurt(node=self.nodes, keys=[upvote_key])
        account = Account(upvote_account, blockchain_instance=blurt)

        # Base vote weight (random 1-3%)
        base_weight = round(random.uniform(1, 3), 2)

        # add bonus weights
        weight = base_weight + delegation_bonus + member_bonus

        if weight > 100.0:
            weight = 100.0

        # TEMP WEIGHT ADJUSTMENT
        weight *= 0.8

        try:
            result = blurt.vote(weight, identifier, account=account)
            vote_result["status"] = True
            vote_result["message"] = f"Upvoted: {result}"
            # vote_result["vote_weight"] = vote_weight + delegation_bonus
            vote_result["vote_weight"] = weight - member_bonus
            vote_result["identifier"] = identifier
        except Exception as err:
            print(err)
            vote_result["message"] = f"Error: Please check your URL {err}"

        return vote_result

    def comment_post(self, vote_data):
        vote_weight = f"{vote_data['vote_weight']:.2f}"
        post_key = Config.UPVOTE_KEY
        username = Config.UPVOTE_ACCOUNT
        B = Blurt(node=self.nodes, keys=[post_key])

        # Get thank you image from giphy
        url = (
            'http://api.giphy.com/v1/gifs/search?'
            'q=arigato thanks heart&'
            'api_key=b2w5nCHfqrGt6tbXBD7BCcfw11plV5b1&'
            'limit=100'
        )
        response = requests.get(url)
        json_data = response.json()

        # Pick a random image data from json_data
        default_img = 'https://i.imgur.com/6qvr7sJ.jpg'
        image_data = random.choice(json_data['data'])
        gif_img = image_data['images']['original']['url']
        gif_img = gif_img.split('?', 1)[0]
        img_url = gif_img or default_img

        comment_body = f"""
{img_url}
** Your post has been upvoted ({vote_weight} %) **
* **Curation Trail Registration is Open!**
[Curation Trail Here](https://blurtblock.herokuapp.com/blurt/trail)

* **Delegate more BP for better Upvote + Daily BLURT** 😉
[Delegate BP Here](https://blurtblock.herokuapp.com/blurt/delegate)

Thank you 🙂 @tomoyan
https://blurtblock.herokuapp.com/blurt/upvote
        """

        # Post a reply comment
        B.post(
            author=username,
            title='comment title',
            body=comment_body,
            reply_identifier=vote_data['identifier'])

    def check_post_vote(self, identifier):
        # check identifier (@username/permalink)
        # if it is already upvoted or not(True/False)
        result = False

        upvote_account = Config.UPVOTE_ACCOUNT
        blurt = Blurt(node=self.nodes)
        account = Account(upvote_account, blockchain_instance=blurt)
        COMMENT = Comment(identifier, api='condenser',
                          blockchain_instance=blurt)

        result = account.has_voted(COMMENT)

        return result

    def check_post_age(self, identifier):
        # if post age is younger than 5 minutes (300 secs)
        # or older than 5 days (432000 secs)
        # return False
        duration_early = 300  # 5 minutes
        duration_late = 432000  # 5 days
        result = False

        COMMENT = Comment(identifier, api='condenser')
        post_age = COMMENT.time_elapsed().total_seconds()

        if duration_early < post_age < duration_late:
            result = True

        return result

    # def check_active_post(self, post_str):
    #     active_posts = []
    #     cashout_time = "1969-12-31T23:59:59"
    #     result = False

    #     strings = post_str.split('/')
    #     username = strings[0]
    #     post_id = strings[1]
    #     blurt = Blurt(node=self.nodes)
    #     blurt_account = Account(username, blockchain_instance=blurt)
    #     posts = blurt_account.get_blog(raw_data=True)

    #     for post in posts:
    #         # post has been paid out
    #         if post["comment"]["cashout_time"] == cashout_time:
    #             continue

    #         if post["blog"]:
    #             active_posts.append(post["comment"]["permlink"])

    #     if post_id in active_posts:
    #         result = True

    #     return result

    def save_data_fb(self, db_name, data):
        # save data into firebase database
        result = self.firebase.child(db_name).push(data)
        return result

    def update_data_fb(self, db_name, key, data):
        # update data into firebase database
        result = self.firebase.child(db_name).child(key).update(data)
        return result

    def get_reward_summary_fb(self, key):
        # get reward summary data and then remove from fb
        result = dict()
        db_name = 'reward_summary'
        data = self.firebase.child(db_name).child(key).get()

        if data.each():
            for d in data.each():
                result[d.key()] = d.val()

        return result

    def remove_reward_summary_fb(self, key):
        # remove reward summary from fb
        db_name = 'reward_summary'
        self.firebase.child(db_name).child(key).remove()

    def get_account_history_fb(self, key):
        # get account history data and then remove from fb
        result = dict()
        db_name = 'account_history'
        data = self.firebase.child(db_name).child(key).get()

        if data.each():
            for d in data.each():
                result[d.key()] = d.val()

        return result

    def remove_account_history_fb(self, key):
        # remove account history from fb
        db_name = 'account_history'
        self.firebase.child(db_name).child(key).remove()

    def process_upvote(self, url):
        username = None
        identifier = None
        now = datetime.utcnow()
        current_time = now.strftime("%m/%d/%Y %H:%M:%S")

        data = {
            'status': False,
            'message': 'Error: Post URL'
        }

        # save client access_data
        access_data = {
            'post_url': url,
            'created': current_time,
            'client_ip': self.client_ip,
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

        # check coal_list
        is_coal = self.is_coal(username)
        if is_coal:
            discord_channel = 'https://discord.gg/PPpZe4eXzf'
            data['message'] = f"""
            Error: This account is coal listed.
            Check out <a href="{discord_channel}">Official Blurt Discord</a>
            for further assistance.
            """
            data['message'] = Markup(data['message'])
            return data

        # check ignore_list
        is_ignored = self.is_ignored(username)
        if is_ignored:
            data['message'] = f'Error: Oops, something went wrong {username}'
            return data

        # check last ip
        used_ip = self.check_last_ip(self.client_ip)
        print(username, used_ip)
        if used_ip is False:
            print('SLOWMODE: ', username)
            data['message'] = 'Error: Slowmode enabled. Come back later!'
            return data

        # check last upvote
        can_vote = self.check_last_upvote(username)
        if can_vote is False:
            wait_message = 'Please come back later'
            data['message'] = f'Error: {wait_message} ({self.wait_time})'
            return data

        # check if post is voted already
        is_voted = self.check_post_vote(identifier)
        if is_voted:
            data['message'] = 'Error: This post has been upvoted already'
            return data

        # check post age
        post_age = self.check_post_age(identifier)
        if post_age is False:
            data['message'] = 'Error: Post has to be 5 minutes old or \
                less than 5 days old'
            return data

        # check post is active
        # active_post = self.check_active_post(strings[1])
        # if active_post is False:
        #     data['message'] = 'Error: This post is too old to upvote'
        #     return data

        # check delegation bonus
        delegation_bonus = self.delegation_bonus(username)

        # check member level bonus
        member_bonus = self.member_bonus(username)

        # check star bonus
        # 2.5 stars -> 25%
        # 5 stars -> 100%
        star_bonus = 0.0
        stars = self.get_star_rating(username)
        if stars == 2.5:
            star_bonus = 25.0
        elif stars == 5.0:
            star_bonus = 100.0
        member_bonus += star_bonus

        bonus_weight = delegation_bonus + member_bonus

        # upvote
        is_upvoted = self.upvote_post(
            identifier, delegation_bonus, member_bonus)
        if is_upvoted["status"] is False:
            data['message'] = is_upvoted["message"]
            return data

        # Leave a comment after upvote
        self.comment_post(is_upvoted)

        # save upvote_data
        upvote_data = {
            'username': username,
            'identifier': identifier,
            'created': current_time,
            'vote_weight': is_upvoted["vote_weight"],
            'bonus_weight': bonus_weight,
            'client_ip': self.client_ip,
        }
        self.save_data_fb("upvote_log", upvote_data)

        data = {
            'status': True,
            'message': 'Thank You. This post has been upvoted.',
            'identifier': identifier
        }

        # UPVOTE REWARD COUNTS
        # increment upvote count if username exists in fb
        # if not, set the count to 1
        db_name = 'upvote_count'
        count_data = {'created': current_time}
        upvote_data = self.firebase.child(db_name).child(username).get()

        if upvote_data.each():
            for user_data in upvote_data.each():
                key = user_data.key()
                value = user_data.val()

                if key == 'count':
                    count_data['count'] = value + 1
        else:
            count_data['count'] = 1

        # save upvote count
        self.firebase.child(db_name).child(username).set(count_data)

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

    def get_delegators(self):
        delegators = []

        # get delegators from firebase
        # and return list of usernames and BPs
        db_name = 'delegation_list'
        data = self.firebase.child(db_name).child('delegators').get()

        for d in data.each():
            delegation_data = {
                'username': d.val()['username'],
                'bp': f'{d.val()["bp"]:,.3f}',
                'timestamp': d.val()['timestamp'],
            }
            delegators.append(delegation_data)

        return delegators

    # OLD delegation list not in use
    def get_delegations(self):
        delegators = []

        # get delegators from firebase
        # and return list of usernames
        db_name = 'delegation_list'
        data = self.firebase.child(db_name).child('list').get()

        for d in data.each():
            username = d.val()['username']
            delegators.append(username)

        return delegators

    def get_leaderboard(self):
        db_name = 'upvote_log'
        logs = self.firebase.child(db_name).get()
        users = {}
        leaderboard = []
        max_users = 50

        for log in logs.each():
            value = log.val()

            if 'vote_weight' not in value:
                continue

            username = value['username']
            vote_weight = value['vote_weight']
            if username in users:
                users[username] += vote_weight
            else:
                users[username] = vote_weight

        # sort users data by total value
        users = dict(sorted(users.items(), reverse=True,
                            key=lambda item: item[1]))

        delegators = self.get_delegators()
        delegators = list(map(itemgetter('username'), delegators))

        max_value = 0.0
        for count, user in enumerate(users):
            if count == 0:
                max_value = users[user]

            if count == max_users:
                break

            leaderboard.append({
                'username': user,
                'points': f'{users[user]:0.2f}',
                'percentage': f'{users[user] / max_value * 100:0.2f}',
                'is_delegator': user in delegators,
            })

        return leaderboard

    def get_ranking(self, user):
        rank = 0
        users = {}
        db_name = 'upvote_log'

        logs = self.firebase.child(db_name).get()
        for log in logs.each():
            value = log.val()
            username = value['username']
            vote_weight = value['vote_weight']

            if username in users:
                users[username] += vote_weight
            else:
                users[username] = vote_weight

        # sort users data by total value
        users = dict(sorted(users.items(), reverse=True,
                            key=lambda item: item[1]))

        users = list(users.keys())
        rank = users.index(user) + 1 if user in users else None

        return rank

    def process_transfers(self, data):
        amount = Amount(data['amount'])

        result = {
            'timestamp': data['timestamp'],
            'from': data['from'],
            'to': data['to'],
            'memo': data['memo'],
            'amount': f'{amount}',
        }

        return result

    def get_star_rating(self, username):
        # get upvote counts from firebase
        # and then convert it to star rating
        db_name = 'upvote_count'
        upvote_data = self.firebase.child(db_name).child(username).get()

        # Full and Half star counts
        full_count = 200  # 100% vote weight
        half_count = 100  # 25%+ vote weight
        stars = 0.0
        count = 0

        if upvote_data.each():
            for user_data in upvote_data.each():
                key = user_data.key()
                value = user_data.val()

                if key == 'count':
                    count = value

        if count > 0:
            if (count % full_count) == 0:
                stars = 100.0 / 20
            elif (count % half_count) == 0:
                stars = 50.0 / 20
            else:
                stars = (count % full_count) / full_count * 5

        return float(f'{stars:.2f}')

    def process_votes(self, data):
        result = {
            'timestamp': data['timestamp'],
            'voter': data['voter'],
            'author': data['author'],
            'permlink': data['permlink'],
            'weight': int(data['weight'] / 100)
        }

        return result

    def process_comments(self, data):
        if data['author'] == self.username:
            return None

        result = {
            'timestamp': data['timestamp'],
            'author': data['author'],
            'permlink': data['permlink'],
            'body': markdown(data['body']),
        }

        return result

    def get_history(self, username, option, duration=5):
        now = datetime.utcnow()
        created = now.strftime("%m/%d/%Y %H:%M:%S")
        result = dict(
            username=username,
            option=option,
            history=[],
            created=created
        )

        options = {
            'transfer': ['transfer'],
            'upvote': ['vote'],
            'comment': ['comment'],
        }

        ops = options[option]
        stop = now - timedelta(days=duration)

        transactions = self.account.history_reverse(
            stop=stop, only_ops=ops)

        history_data = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            if option == 'transfer':
                transfers = executor.map(self.process_transfers, transactions)
                for transfer in transfers:
                    history_data.append(transfer)
            elif option == 'upvote':
                upvotes = executor.map(self.process_votes, transactions)
                for upvote in upvotes:
                    history_data.append(upvote)
            elif option == 'comment':
                comments = executor.map(self.process_comments, transactions)
                for comment in comments:
                    if comment:
                        history_data.append(comment)
            else:
                pass

        if history_data:
            result['history'] = sorted(
                history_data, key=itemgetter('timestamp'), reverse=True)

            # save account history data into firebase
            db_name = 'account_history'
            db_key = f'{self.username}_history_{option}'
            self.update_data_fb(db_name, db_key, result)

        return result

    # def get_upvote_data(self, username):
    #     vote_data = {}
    #     chart_data = {
    #         'label': [],
    #         'voteCount': [],
    #         'voteWeight': [],
    #         'totalVote': 0
    #     }

    #     # get user's upvote history and save label, counts and weights
    #     duration = 7
    #     stop = datetime.utcnow() - timedelta(days=duration)
    #     ops = ['vote']
    #     transactions = self.account.history_reverse(
    #         stop=stop, only_ops=ops)

    #     for tx in transactions:
    #         if tx['voter'] != username:
    #             continue

    #         if tx['author'] in vote_data:
    #             vote_data[tx['author']].append(tx['weight'])
    #         else:
    #             vote_data[tx['author']] = [tx['weight']]

    #         chart_data['totalVote'] += 1

    #     # calculate vote weight average
    #     for key, value in vote_data.items():
    #         count = len(value)
    #         weight = (sum(value) / count) // 100
    #         chart_data['label'].append(key)
    #         chart_data['voteCount'].append(count)
    #         chart_data['voteWeight'].append(weight)

    #     return chart_data

    def _process_vote(self, data):
        if data['voter'] != self.username:
            return None
        else:
            return data

    def get_upvote_data(self, username):
        vote_data = {}
        chart_data = {
            'label': [],
            'voteCount': [],
            'voteWeight': [],
            'totalVote': 0
        }

        # get user's upvote history and save label, counts and weights
        duration = 7
        stop = datetime.utcnow() - timedelta(days=duration)
        ops = ['vote']
        transactions = self.account.history_reverse(
            stop=stop, only_ops=ops)

        # go through vote transactions and get voting data
        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = executor.map(self._process_vote, transactions)

            # filter out None from results
            results = list(filter(None, results))

            for tx in results:
                if tx['author'] in vote_data:
                    vote_data[tx['author']].append(tx['weight'])
                else:
                    vote_data[tx['author']] = [tx['weight']]

                chart_data['totalVote'] += 1

            # calculate vote weight average
            for key, value in vote_data.items():
                count = len(value)
                weight = (sum(value) / count) // 100
                chart_data['label'].append(key)
                chart_data['voteCount'].append(count)
                chart_data['voteWeight'].append(weight)

        return chart_data

    def process_rewards(self, data):
        # get reward history data
        # and sums up each reward in vests
        vests = {
            'author_reward_vests': Amount("0 VESTS"),
            'curation_reward_vests': Amount("0 VESTS"),
            'producer_reward_vests': Amount("0 VESTS"),
        }

        ops = ['author_reward', 'curation_reward', 'producer_reward']
        transactions = self.account.history_reverse(
            start=data['start'], stop=data['stop'], only_ops=ops)

        for tx in transactions:
            if tx['type'] == 'author_reward':
                vesting_payout = tx['vesting_payout']
                vests['author_reward_vests'] += Amount(vesting_payout)
            elif tx['type'] == 'curation_reward':
                reward = tx['reward']
                vests['curation_reward_vests'] += Amount(reward)
            elif tx['type'] == 'producer_reward':
                vesting_shares = tx['vesting_shares']
                vests['producer_reward_vests'] += Amount(vesting_shares)

        return vests

    def get_rewards(self, duration=1):
        # get author, curation, producer rewards
        # using threads
        dates = []

        # reward BPs
        data = {
            'author': f'{0.0:,.3f}',
            'curation': f'{0.0:,.3f}',
            'producer': f'{0.0:,.3f}',
            'total': f'{0.0:,.3f}',
        }

        if self.username is None:
            return data

        if duration < 1 or duration > 30:
            duration = 1

        now = datetime.utcnow()

        # duration is divided into 7days or less
        # and stored in dates for history_reverse()
        for i in range(0, duration, 7):
            start = now - timedelta(days=i)
            delta = i + 7
            if delta > duration:
                delta = duration
            stop = now - timedelta(days=delta)
            dates.append({'start': start, 'stop': stop})

        # calling process_rewards() and get BPs
        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = executor.map(self.process_rewards, dates)

            author_total_vests = Amount("0 VESTS")
            curation_total_vests = Amount("0 VESTS")
            producer_total_vests = Amount("0 VESTS")
            for result in results:
                author_total_vests += Amount(result['author_reward_vests'])
                curation_total_vests += Amount(result['curation_reward_vests'])
                producer_total_vests += Amount(result['producer_reward_vests'])

            try:
                author = self.blurt.vests_to_bp(author_total_vests)
            except TypeError:
                author = 0

            try:
                curation = self.blurt.vests_to_bp(curation_total_vests)
            except TypeError:
                curation = 0

            try:
                producer = self.blurt.vests_to_bp(producer_total_vests)
            except TypeError:
                producer = 0

            total = author + curation + producer

            data['total'] = f"{total:,.3f}"
            data['author'] = f"{author:,.3f}"
            data['curation'] = f"{curation:,.3f}"
            data['producer'] = f"{producer:,.3f}"

        # save reward data into firebase
        db_name = 'reward_summary'
        db_key = f'{self.username}_reward_{duration}'
        self.update_data_fb(db_name, db_key, data)

        return data

    def leave_trail(self, username):
        db_name = 'trail_followers'
        result = {
            'status': 0,
            'heading': 'Oops! Something went wrong.',
            'message': 'Error: ',
        }

        if self.username is None:
            result['message'] += 'Account not found'
            return result

        current_time = datetime.utcnow().strftime("%m/%d/%Y %H:%M:%S")

        follow_key = self.get_follow_key(username)
        if follow_key:
            trail_data = {
                'username': username,
                'created': current_time,
                'status': 0,
            }
            self.update_data_fb(db_name, follow_key, trail_data)

            result['status'] = 1
            result['heading'] = 'Successfully removed from the trail'
            result['message'] = 'Come back anytime! 😉'
        else:
            result['message'] += 'Account not found'

        return result

    def join_trail(self, username, posting, weight):
        db_name = 'trail_followers'
        result = {
            'status': 0,
            'heading': 'Oops! Something went wrong.',
            'message': 'Error: '
        }

        if self.username is None:
            result['message'] += 'Account not found'
            return result

        current_time = datetime.utcnow().strftime("%m/%d/%Y %H:%M:%S")

        message = self.decode_message(posting)

        is_verified = self.verify_key(username, message)
        if is_verified['status'] is False:
            result = is_verified
            return result

        trail_data = {
            'username': username,
            'posting': self.encrypt_message(message),
            'created': current_time,
            'weight': weight,
            'status': 1,
        }

        # check if follower exists in fb
        follow_key = self.get_follow_key(username)
        if follow_key:
            self.update_data_fb(db_name, follow_key, trail_data)
        else:
            self.save_data_fb(db_name, trail_data)

        result['status'] = 1
        result['heading'] = 'Successfully join the trail'
        result['message'] = 'Welcome in! 🤩'

        return result

    def decode_message(self, posting):
        message_bytes = base64.b64decode(posting)
        message = message_bytes.decode('ascii')[3:-1]

        return message

    def encrypt_message(self, posting):
        message = cryptocode.encrypt(posting, Config.FB_SERVICEACCOUNT)

        return message

    def decrypt_message(self, posting):
        message = cryptocode.decrypt(posting, Config.FB_SERVICEACCOUNT)

        return message

    def verify_key(self, username, posting):
        result = {
            'status': False,
            'message': 'Error: '
        }

        try:
            blurt = Blurt(node=self.nodes, keys=[posting])
        except Exception as err:
            result['message'] += f'Invalid wif {str(err)}'
            return result

        try:
            public_key = str(PrivateKey(posting).pubkey)
        except Exception as err:
            result['message'] += f'Private key error {str(err)}'
            return result

        acc = Account(username, blockchain_instance=blurt)
        public_auth = str(acc['posting']['key_auths'][0][0])

        # Compare public and private post keys
        if public_key[3:] == public_auth[3:]:
            result['status'] = True
            result['message'] = 'OK'
        else:
            result['message'] += 'Wrong Private Key'

        return result

    def get_follow_key(self, username):
        # Returns fb key if already exists
        result = None
        db_name = 'trail_followers'

        followers = self.firebase.child(db_name).get()

        if followers.val():
            for data in followers.each():
                if data.val()['username'] == username:
                    result = data.key()

        return result

    def trail_upvote(self, identifier=None):
        weight = 100.0
        voting_power = 80.0
        db_name = 'trail_followers'

        followers = self.firebase.child(
            db_name).order_by_child("status").equal_to(1).get()

        for follower in followers.each():
            username = follower.val()['username']
            posting = self.decrypt_message(follower.val()['posting'])
            weight = follower.val()['weight']

            try:
                BLT = Blurt(self.nodes, keys=[posting])
                ACC = Account(username, blockchain_instance=BLT)
                if ACC.get_voting_power() < voting_power:
                    continue

                COMMENT = Comment(
                    identifier, api='condenser', blockchain_instance=BLT)
                if ACC.has_voted(COMMENT):
                    print('ALREADY_VOTED', ACC, identifier)
                    continue
                print(username, weight)
                BLT.vote(weight, identifier, account=ACC)
            except Exception as err:
                print('TRAIL_VOTE_ERR', username, err)

    def get_trail_count(self):
        db_name = 'trail_followers'
        data = {'count': 0}

        followers = self.firebase.child(
            db_name).order_by_child("status").equal_to(1).get()

        data['count'] = len(followers.val())

        return data
