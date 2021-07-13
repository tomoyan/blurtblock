from beem import Blurt
from beem.account import Account
import os

# Setup blurt nodes and account
BLURT_NODES = ['https://rpc.blurt.world']
USERNAME = os.environ.get('USERNAME')
UPVOTE_KEY = os.environ.get('POST_KEY')
BLURT = Blurt(BLURT_NODES, keys=[UPVOTE_KEY])
ACCOUNT = Account(USERNAME, blockchain_instance=BLURT)


def main():
    # Upvote my own posts automatically
    # Script runs after daily delegation report
    upvote_blog_entries()


def upvote_blog_entries():
    # Get my last 7 blog posts
    # Upvote them if they are not voted
    posts = ACCOUNT.blog_history(limit=7, reblogs=False)

    for post in posts:
        voted = ACCOUNT.has_voted(post)

        # 100% Upvote if post hasn't been voted
        if not voted:
            weight = 100.0
            identifier = post.authorperm
            # Upvote a post
            BLURT.vote(weight, identifier, account=ACCOUNT)


if __name__ == '__main__':
    main()
