import os
import time
import requests
from datetime import datetime, timedelta
from beem.account import Account
from _steem import get_steem

COMMUNITY_NAME = os.environ.get('COMMUNITY_NAME')
COMMUNITY_POST_KEY = os.environ.get('COMMUNITY_POST_KEY')
STEEM = get_steem(COMMUNITY_POST_KEY)
ACCOUNT = Account(COMMUNITY_NAME, blockchain_instance=STEEM)


def get_sds_data(url):
    # get request to sds.steemworld.org
    json_data = {}

    response = requests.get(url)
    if response:
        json_data = response.json()

    return json_data


def get_community_posts():
    posts = []
    authors = []
    muted_members = get_muted_members()

    # last 24h data
    start_epoch = datetime.now() - timedelta(days=1)
    start_epoch = start_epoch.timestamp()

    url = (
        'https://sds.steemworld.org'
        '/feeds_api'
        '/getCommunityPostsByCreated'
        '/hive-161179'
    )
    json_data = get_sds_data(url)
    community_posts = json_data['result']['rows']

    for post in community_posts:
        # Skip is_muted members
        if post[13] or post[18] in muted_members:
            continue

        # Check duplicate author
        if post[18] in authors:
            continue

            # Only 24h posts
        if post[3] > start_epoch:
            date = datetime.fromtimestamp(post[3])
            sp = check_delegation_sp(post[18])

            posts.append({
                'date': date,
                'author': post[18],
                'permlink': post[19],
                'title': post[20],
                'sp': sp
            })

            authors.append(post[18])
        else:
            break

    return posts


def check_delegation_sp(username):
    sp = 0
    url = (
        'https://sds.steemworld.org'
        '/delegations_api'
        '/getOutgoingDelegations'
        f'/{username}'
    )
    json_data = get_sds_data(url)
    delegations = json_data['result']['rows']

    for delegation in delegations:
        if delegation[2] == 'japansteemit':
            sp = int(STEEM.vests_to_sp(delegation[3]))
            break

    return sp


def upvote_posts(posts):
    for post in posts:
        if not post['sp']:
            continue

        weight = post['sp'] // 10
        if weight > 100:
            weight = 100
        identifier = f"@{post['author']}/{post['permlink']}"

        if ACCOUNT.has_voted(identifier):
            print('ALREADY VOTED', identifier)
            continue

        try:
            print('VOTE', identifier, weight)
            STEEM.vote(weight, identifier, ACCOUNT)
        except Exception as err:
            print('UPVOTE_ERR', err, identifier)

        time.sleep(3)


def get_muted_members():
    muted_members = []
    url = (
        'https://sds.steemworld.org'
        '/communities_api'
        '/getCommunityRoles'
        '/hive-161179'
    )
    json_data = get_sds_data(url)
    rows = json_data['result']['rows']

    for row in rows:
        if row[-1] == 'muted':
            muted_members.append(row[1])

    return muted_members


def main():
    print('START_UPVOTE_COMMUNITY_POSTS')

    posts = get_community_posts()
    upvote_posts(posts)

    print('END_UPVOTE_COMMUNITY_POSTS')


if __name__ == '__main__':
    main()
