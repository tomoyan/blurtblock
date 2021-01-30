from beem import Blurt
from pprint import pprint
from datetime import datetime
import os


def main():
    today = datetime.now().strftime("%Y-%m-%d")
    post_data = {
        'title': f'Title Test - {today}',
        'body': f'POST BODY HERE',
        'tags': ["blurtblock", "rewards", "blurt"],
    }

    publish_post(post_data)


def publish_post(data):
    username = os.environ.get('POST_ACCOUNT')
    key = os.environ.get('POST_KEY')

    blurt_nodes = ['https://rpc.blurt.world']
    blurt = Blurt(blurt_nodes, keys=[key])

    result = blurt.post(
        author=username,
        title=data['title'],
        body=data['body'],
        tags=data['tags'],
        self_vote=False)

    pprint(result)


if __name__ == '__main__':
    main()
