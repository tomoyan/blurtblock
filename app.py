# from beem.account import Account
# from beem.amount import Amount
# from beem.instance import set_shared_blockchain_instance
# from datetime import datetime, timedelta
# import logging

from flask import Flask, render_template, redirect, request, flash, jsonify
from config import Config
from forms import UserNameForm
from markupsafe import escape
from flask_talisman import Talisman

import BlurtChain as BC


app = Flask(__name__)
app.config.from_object(Config)

# Forces all connects to https, unless running with debug enabled.
talisman = Talisman(app)
talisman.content_security_policy_report_only = True


@app.errorhandler(404)
# This handles 404 error
def page_not_found(e):
    return render_template('404.html')


# @app.route('/')
# def home():
#     return render_template('index.html')


# @app.route('/blurt', methods=['GET', 'POST'])
# @app.route('/blurt/', methods=['GET', 'POST'])
@app.route('/', methods=['GET', 'POST'])
def blurt():
    form = UserNameForm(request.form)

    if request.method == 'POST':
        if form.validate():
            username = request.form['username'].lower()

            return redirect(f'/{username}')
        else:
            flash('Username is Required')

    return render_template('blurt/profile.html', form=form)


# @app.route('/blurt/<username>')
# @app.route('/blurt/<username>/')
@app.route('/<username>')
@app.route('/<username>/')
def blurt_profile_data(username=None):
    # print(f'BLURT_PROFILE_DATA USERNAME: {username}')
    data = {}
    if username:
        username = escape(username).lower()
        blurt = BC.BlurtChain(username)

        data = blurt.get_account_info()
        vote_data = blurt.get_vote_history()
        data['labels'] = vote_data['labels']
        data['permlinks'] = vote_data['permlinks']
        data['count_data'] = vote_data['count_data']
        data['weight_data'] = vote_data['weight_data']
        data['total_votes'] = vote_data['total_votes']
        # print(f'GET_ACCOUNT_INFO: {data}')
    return render_template('blurt/profile_data.html',
                           username=blurt.username, data=data)


# BLURT API
@app.route('/api/blurt/follower/<username>')
@app.route('/api/blurt/follower/<username>/')
def blurt_follower(username=None):
    # print('BLURT_FOLLOWER_DEF')
    data = {}
    if username:
        blurt = BC.BlurtChain(username)
        data = blurt.get_follower()
        # print('BLURT_FOLLOWER', vars(blurt))
    return jsonify(data)


@app.route('/api/blurt/following/<username>')
@app.route('/api/blurt/following/<username>/')
def blurt_following(username=None):
    # print('BLURT_FOLLOWING_DEF')
    data = {}
    if username:
        blurt = BC.BlurtChain(username)
        data = blurt.get_following()

    return jsonify(data)


@app.route('/api/blurt/votes/<username>')
@app.route('/api/blurt/votes/<username>/')
def blurt_votes(username=None):
    data = {}
    if username:
        blurt = BC.BlurtChain(username)
        data = blurt.get_vote_history()

    return jsonify(data)


@app.route('/api/blurt/mute/<username>')
@app.route('/api/blurt/mute/<username>/')
def blurt_mute(username=None):
    data = {}
    if username:
        blurt = BC.BlurtChain(username)
        data = blurt.get_mute()

    return jsonify(data)


@app.route('/api/blurt/delegation/<username>')
@app.route('/api/blurt/delegation/<username>/')
def blurt_delegation(username=None):
    data = {}
    if username:
        blurt = BC.BlurtChain(username)
        data = blurt.get_delegation()

    return jsonify(data)


@app.route('/api/blurt/reward/<username>')
@app.route('/api/blurt/reward/<username>/')
def blurt_reward(username=None):
    data = {}
    if username:
        blurt = BC.BlurtChain(username)
        data = blurt.get_reward_summary()

    return jsonify(data)


if __name__ == "__main__":
    # app.run()
    app.run(debug=True)
