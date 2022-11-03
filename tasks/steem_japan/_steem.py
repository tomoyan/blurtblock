from beem import Steem
from beem.instance import set_shared_blockchain_instance

import random
import requests

NODES = [
    'https://api.steemit.com',
    'https://api.steem.buzz',
    'https://steem.61bts.com'
    # 'https://steem.moonjp.xyz',
]


def get_node():
    random.shuffle(NODES)
    result = NODES[0]

    for node in NODES:
        try:
            response = requests.get(node, timeout=1)
            if response:
                result = node
                break
        except requests.exceptions.RequestException as e:
            print(f'GET_NODE_ERR:{node} {e}')

    return result


def get_steem(*args):
    # get_steem takes post key, active key or no key
    keys = [*args]
    STEEM = Steem(node=get_node(), keys=keys)
    set_shared_blockchain_instance(STEEM)

    return STEEM


if __name__ == '__main__':
    # get_steem('5KhdrAo5kDSEVDEDcSs5wd64pup5jyJQdTWr4yqyRTtZgVH3ydT')
    # get_steem('5KcgCitGSbC3K88J8ZbU8Fe4MnMch7LZ74V9PSavdqweY9RzYJM')
    # get_steem(
    #     '5KcgCitGSbC3K88J8ZbU8Fe4MnMch7LZ74V9PSavdqweY9RzYJM',
    #     '5KhdrAo5kDSEVDEDcSs5wd64pup5jyJQdTWr4yqyRTtZgVH3ydT')
    get_steem()
