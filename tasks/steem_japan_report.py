from pprint import pprint
from datetime import datetime
import os

from beem import Steem
from beem.nodelist import NodeList
from beem.discussions import Query, Discussions_by_created


# Setup Steem nodes
nodelist = NodeList()
nodelist.update_nodes()
nodes = nodelist.get_steem_nodes()

POST_KEY = os.environ.get('POST_KEY')
USERNAME = os.environ.get('USERNAME')
STEEM = Steem(node=nodes, keys=[POST_KEY])


def main():
    # Japan Time(JST) 12AM is 3PM in UTC
    discussions = get_discussions()

    # Community activity stats
    stats = get_stats(discussions)

    publish_post(stats)


def get_stats(discussions):
    data = dict()
    active_members = []
    total_posts = 0
    total_votes = 0
    total_comments = 0

    # Find active members and posts for the day
    for d in discussions:
        username = d.author
        if username not in data.keys():
            data[username] = {
                'posts': [d.permlink],
                'votes': 0,
                'comments': 0,
            }
            total_posts += 1
            continue

        data[username]['posts'].append(d.permlink)
        total_posts += 1

    active_members = data.keys()

    # Find number of comments/votes to active members
    for d in discussions:
        # Check comments
        replies = d.get_all_replies()
        for reply in replies:
            if reply.author in active_members:
                data[reply.author]['comments'] += 1
                total_comments += 1

        # Check votes
        voters = d.get_votes().get_list()
        for username in voters:
            if username in active_members:
                data[username]['votes'] += 1
                total_votes += 1

    return {
        'stats': data,
        'total_posts': total_posts,
        'total_votes': total_votes,
        'total_comments': total_comments
    }


def get_discussions():
    # Get community posts for the last 24 hours
    discussions = []
    steem_japan = 'hive-161179'
    duration = 86400  # 1 day in seconds

    q = Query(limit=100, tag=steem_japan)
    # Save discussions that are less than 1 day old
    for d in Discussions_by_created(q):
        if d.time_elapsed().total_seconds() < duration:
            discussions.append(d)

    return discussions


def get_post_body(data):
    sp_url = 'https://steemlogin.com/sign/delegateVestingShares?delegator=&delegatee=japansteemit&vesting_shares='
    community_url = 'https://steemit.com/created/hive-161179'
    trail_url = 'https://worldofxpilar.com/dash.php?i=1&trail=japansteemit'
    trail_info = 'https://steemit.com/@tomoyan/steem-japan-join-new-curation-trail'
    stats_table = """
| Avatar | Member | Post # | Comment # | Vote # |
| --- | --- | --- | --- | --- |
    """

    for d in data['stats']:
        avatar = f"<img src='https://steemitimages.com/u/{d}/avatar/small'>"
        member = d
        post = len(data['stats'][d]['posts'])
        comment = data['stats'][d]['comments']
        vote = data['stats'][d]['votes']
        stats_table += f"|{avatar}|{member}|{post}|{comment}|{vote}|\n"

    body = f"""
![](https://i.imgur.com/wOSnnYI.png)

### Steem Japan コミュニティーメンバーの活動状況デイリーレポート
コミュニティー内で誰がどれだけアクティブに活動し、記事の投稿、他のコミュニティーメンバーにコメント・アップボートしているかなど、
コミュニティー貢献度が一目で分かるように情報をレポート化。

## [Steem Japan]({community_url}) Members Daily Activities
* Total Posts: {data['total_posts']}
* Total Comments: {data['total_comments']}
* Total Votes: {data['total_votes']}

**投稿メンバーのアクティビティー情報**
**Active Posting Members Info**

{stats_table}

**今後のコンテストにはコミュニティーメンバーの活動状況が考慮されるかも🤔**

---
### * Follow @japansteemit community curation trail
**キュレーショントレールをフォローしよう！**
Curation trail is here 👇:
{trail_url}
[![](https://i.imgur.com/0wVb3qI.png)]({trail_url})
Curation trail info 👇:
{trail_info}

### * Delegate STEEM POWER to @japansteemit
**@japansteemitにSPをデレゲーションしよう！**
| Click | And | Delegate | SP | Here 👇 |
| --- | --- | --- | --- | --- |
|[100 SP]({sp_url}100%20SP)|[500 SP]({sp_url}500%20SP)|[1000 SP]({sp_url}1000%20SP)|[2000 SP]({sp_url}2000%20SP)|[3000 SP]({sp_url}3000%20SP)|

### * [Join Steem Japan Discord (ディスコードサーバー)](https://discord.gg/pE5fuktSAt)
[![](https://i.imgur.com/xADG309.png)](https://steemit.com/@japansteemit)
    """

    return body


def publish_post(stats):
    today = datetime.utcnow().strftime("%Y-%m-%d")

    title = f'Steem Japan: Community Member Stats {today}'
    tags = ['hive-161179', 'steem', 'japan', 'community', 'stats']
    body = get_post_body(stats)

    STEEM.post(
        author='tomoyan',
        title=title,
        body=body,
        tags=tags,
        self_vote=False)


if __name__ == '__main__':
    main()
