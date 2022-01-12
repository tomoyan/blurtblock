from beem import Blurt
from beem.account import Account
import os
import requests

# Setup blurt nodes and account
BLURT_NODES = ['https://rpc.blurt.world']
USERNAME = os.environ.get('USERNAME')
UPVOTE_KEY = os.environ.get('POST_KEY')
BLURT = Blurt(BLURT_NODES, keys=[UPVOTE_KEY])
ACCOUNT = Account(USERNAME, blockchain_instance=BLURT)

# 100% Upvote for special users
USERS = [
    'ecosynthesizer', 'maxinpower', 'the-gorilla', 'tomoyan',
    'kahkashanrkploy', 'kamranrkploy'
]


def main():
    for user in USERS:
        upvote_blog_entries_username(user)


def upvote_blog_entries_username(name):
    ACCT = Account(name, blockchain_instance=BLURT)
    posts = ACCT.blog_history(limit=1, reblogs=False)

    for post in posts:
        voted = ACCOUNT.has_voted(post)

        if not voted:
            weight = 85.0
            if name == 'ecosynthesizer':
                weight = 35.0
            elif name == 'tomoyan':
                weight = 100.0
            elif name == 'kahkashanrkploy':
                weight = 50.0
            elif name == 'kamranrkploy':
                weight = 50.0

            identifier = post.authorperm
            # Upvote a post
            BLURT.vote(weight, identifier, account=ACCOUNT)

            # Trail vote API
            # https://blurtblock.herokuapp.com/api/blurt/trail-vote/?id=@user/id
            base_url = 'https://blurtblock.herokuapp.com'
            url = (
                f'{base_url}'
                '/api/blurt/trail-vote/?'
                f'id={identifier}'
            )
            requests.get(url)


if __name__ == '__main__':
    main()
