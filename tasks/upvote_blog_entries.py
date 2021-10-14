from beem import Blurt
from beem.account import Account
import os

# Setup blurt nodes and account
BLURT_NODES = ['https://rpc.blurt.world']
USERNAME = os.environ.get('USERNAME')
UPVOTE_KEY = os.environ.get('POST_KEY')
BLURT = Blurt(BLURT_NODES, keys=[UPVOTE_KEY])
ACCOUNT = Account(USERNAME, blockchain_instance=BLURT)

# 100% Upvote for special users
USERS = ['ecosynthesizer', 'maxinpower']


def main():
    for user in USERS:
        upvote_blog_entries_username(user)


def upvote_blog_entries_username(name):
    ACCT = Account(name, blockchain_instance=BLURT)
    posts = ACCT.blog_history(limit=3, reblogs=False)

    for post in posts:
        voted = ACCOUNT.has_voted(post)

        if not voted:
            weight = 100.0
            identifier = post.authorperm
            # Upvote a post
            BLURT.vote(weight, identifier, account=ACCOUNT)


if __name__ == '__main__':
    main()
