from flask import Flask, render_template, redirect, request, flash, jsonify
from config import Config
from forms import UserNameForm
from markupsafe import escape
from flask_talisman import Talisman
import ast

import BlurtChain as BC


app = Flask(__name__)
app.config.from_object(Config)

# Forces all connects to https, unless running with debug enabled.
# csp = {
#     'default-src': '\'self\'',
#     'img-src': '*',
#     'style-src': '*',
#     'connect-src': '*',
#     'force_https': 'False'
# }
# talisman = Talisman(app, content_security_policy=csp)
talisman = Talisman(app)
talisman.content_security_policy_report_only = True


@app.errorhandler(404)
# This handles 404 error
def page_not_found(e):
    return render_template('404.html')


# @app.route('/')
# def home():
#     return render_template('index.html')


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


@app.route('/<username>')
@app.route('/<username>/')
def blurt_profile_data(username=None):
    data = {}
    if username:
        username = escape(username).lower()
        blurt = BC.BlurtChain(username)

        data = blurt.get_account_info()
        vote_data = blurt.get_vote_history()
        data['labels'] = vote_data['labels']
        data['permlinks'] = vote_data['permlinks']
        data['upvotes'] = vote_data['upvotes']
        data['count_data'] = vote_data['count_data']
        data['weight_data'] = vote_data['weight_data']
        data['total_votes'] = vote_data['total_votes']

    return render_template('blurt/profile_data.html',
                           username=blurt.username, data=data)


@app.route('/blurt/stats')
@app.route('/blurt/stats/')
def stats():
    blurt = BC.BlurtChain(username=None)
    stats_data = blurt.get_stats()

    return render_template('blurt/stats.html', data=stats_data)


@app.route('/blurt/upvote')
@app.route('/blurt/upvote/')
def upvote():
    return render_template('blurt/upvote.html')


# BLURT API
@app.route('/api/blurt/follower/<username>')
@app.route('/api/blurt/follower/<username>/')
def blurt_follower(username=None):
    data = {}
    if username:
        blurt = BC.BlurtChain(username)
        data = blurt.get_follower()

    return jsonify(data)


@app.route('/api/blurt/following/<username>')
@app.route('/api/blurt/following/<username>/')
def blurt_following(username=None):
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
    app.run()
    # app.run(debug=True)
