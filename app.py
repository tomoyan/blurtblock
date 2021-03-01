from flask import Flask, render_template, redirect, request, flash, jsonify
from flask import session
from flask_session import Session

from config import Config
from forms import UserNameForm
from forms import postUrlForm
from markupsafe import escape
import BlurtChain as BC
from multiprocessing import Process

app = Flask(__name__)
app.config.from_object(Config)
Session(app)


@app.errorhandler(404)
# This handles 404 error
def page_not_found(e):
    return render_template('404.html')


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

        # check session profile_data
        profile_data = username + '_profile_data'
        if session.get(profile_data):
            data = session[profile_data]
        else:
            data = blurt.get_account_info()
            session[profile_data] = data

        data['stars'] = 0

        # process 30 day reward summary in the background
        p1 = Process(target=blurt_reward, args=[username, 30])
        p1.start()

    return render_template('blurt/profile_data.html',
                           username=blurt.username, data=data)


@app.route('/blurt/upvote', methods=['GET', 'POST'])
@app.route('/blurt/upvote/', methods=['GET', 'POST'])
def upvote():
    form = postUrlForm(request.form)
    data = {
        'banner': 'publish0x'
    }

    if request.method == 'POST':
        if form.validate():
            url = request.form['url'].lower()
            blurt = BC.BlurtChain(username=None)

            forwarded_for = request.headers.getlist("X-Forwarded-For")
            blurt.client_ip = ''
            if forwarded_for:
                blurt.client_ip = forwarded_for[0]

            result = blurt.process_upvote(url)
            flash(result['message'])
        else:
            # check empty url
            flash('Error: URL is required')

    return render_template('blurt/upvote.html', form=form, data=data)


@app.route('/blurt/leaderboard')
@app.route('/blurt/leaderboard/')
def leaderboard(username=None):
    data = {}

    blurt = BC.BlurtChain(username)
    data = blurt.get_leaderboard()

    return render_template('blurt/leaderboard.html',
                           data=data)


@app.route('/blurt/delegators')
@app.route('/blurt/delegators/')
def delegators(username=None):
    data = {}

    blurt = BC.BlurtChain(username)
    data = blurt.get_delegators()

    return render_template('blurt/delegators.html',
                           data=data)


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


@app.route('/api/blurt/delegation/<username>/<option>')
@app.route('/api/blurt/delegation/<username>/<option>/')
def blurt_delegation(username=None, option=None):
    delegation_type = ["in", "out", "exp"]
    data = {}
    if username and option in delegation_type:
        # check session delegation_data
        delegation_data = username + '_delegation_' + option
        if session.get(delegation_data):
            data = session[delegation_data]
        else:
            blurt = BC.BlurtChain(username)
            data = blurt.get_delegation_new(option)
            session[delegation_data] = data

    return jsonify(data)


@app.route('/api/blurt/reward/<username>/<int:duration>')
@app.route('/api/blurt/reward/<username>/<int:duration>/')
@app.route('/api/blurt/reward/<username>/<int:duration>/<option>')
@app.route('/api/blurt/reward/<username>/<int:duration>/<option>/')
def blurt_reward(username=None, duration=1, option=None):
    data = {}
    if username:
        blurt = BC.BlurtChain(username)
        # check session reward_data
        reward_data = username + '_reward_' + str(duration)
        if session.get(reward_data):
            data = session[reward_data]
            blurt.remove_reward_summary_fb(reward_data)
        else:
            data = blurt.get_reward_summary_fb(reward_data)
            session[reward_data] = data
            blurt.remove_reward_summary_fb(reward_data)

            if not data:
                data = blurt.get_reward_summary(duration, option=option)
                session[reward_data] = data

    return jsonify(data)


@app.route('/api/blurt/author_reward/<username>/<int:duration>')
@app.route('/api/blurt/author_reward/<username>/<int:duration>/')
def blurt_author(username=None, duration=1):
    data = None
    if username:
        blurt = BC.BlurtChain(username)

        # check session reward_data
        reward_data = username + '_author_reward_' + str(duration)
        if session.get(reward_data):
            data = session[reward_data]
        else:
            data = blurt.get_author_reward(duration)
            if data != "0.0":
                session[reward_data] = data

    return jsonify(data)


@app.route('/api/blurt/curation_reward/<username>/<int:duration>')
@app.route('/api/blurt/curation_reward/<username>/<int:duration>/')
def blurt_curation(username=None, duration=1):
    data = None
    if username:
        blurt = BC.BlurtChain(username)

        # check session reward_data
        reward_data = username + '_curation_reward_' + str(duration)
        if session.get(reward_data):
            data = session[reward_data]
        else:
            data = blurt.get_curation_reward(duration)
            if data != "0.0":
                session[reward_data] = data

    return jsonify(data)


@app.route('/api/blurt/producer_reward/<username>/<int:duration>')
@app.route('/api/blurt/producer_reward/<username>/<int:duration>/')
def blurt_producer(username=None, duration=1):
    data = None
    if username:
        blurt = BC.BlurtChain(username)

        # check session reward_data
        reward_data = username + '_producer_reward_' + str(duration)
        if session.get(reward_data):
            data = session[reward_data]
        else:
            data = blurt.get_producer_reward(duration)
            if data != "0.0":
                session[reward_data] = data

    return jsonify(data)


@app.route('/api/blurt/leaderboard')
@app.route('/api/blurt/leaderboard/')
def blurt_leaderboard(username=None):
    data = {}

    blurt = BC.BlurtChain(username)
    data = blurt.get_leaderboard()

    return jsonify(data)


@app.route('/api/blurt/ranking/<username>')
@app.route('/api/blurt/ranking/<username>/')
def blurt_ranking(username=None):
    data = {}
    if username:
        blurt = BC.BlurtChain(username)
        data = blurt.get_ranking(username)

    return jsonify(data)


@app.route('/api/blurt/history/<username>/<string:option>')
@app.route('/api/blurt/history/<username>/<string:option>/')
def blurt_history(username=None, option=None):
    data = dict()

    if username and option:
        blurt = BC.BlurtChain(username)

        # check session history_data
        history_data = username + '_history_' + str(option)
        if session.get(history_data):
            data = session[history_data]
        else:
            data = blurt.get_history(username, option)
            session[history_data] = data

    return jsonify(data)


@app.route('/api/blurt/votedata/<username>')
@app.route('/api/blurt/votedata/<username>/')
def blurt_votedata(username=None):
    data = {}
    if username:
        blurt = BC.BlurtChain(username)

        # check session data
        vote_data = username + '_votedata'

        if session.get(vote_data):
            data = session[vote_data]
        else:
            data = blurt.get_upvote_data(username)
            session[vote_data] = data

    return jsonify(data)


if __name__ == "__main__":
    app.run()
