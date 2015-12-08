"""
Routes and views for the flask application.
"""


import uuid
from flask import Flask
from flask.ext.jsonpify import jsonify
from flask import render_template, request
import os
import redis


redis_url = os.getenv('REDISCLOUD_URL', 'redis://localhost:6379')
redis = redis.from_url(redis_url)

import imp    
actions = imp.load_source('core.actions', 'core/actions.py')

import json

from flask import Flask
app = Flask(__name__)


#sessions = {}


def get_session(session_id):
    print "Retrieving session: %s" % session_id
    session_data = redis.get(session_id)
    return session_id


def save_session(session_data):
    session_id = str(uuid.uuid4())
    redis.set(session_id, session_data)
    #sessions[session_id] = session_data
    print "Saving session: %s" % session_id
    return session_id
    
#TODO: def end_session


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/sessions/<session_id>/new', methods=['GET'])
def new(session_id):
    # remove old session
    #sessions.pop(session_id, None)
    _session_data = actions.create_session_data()
    sid = save_session(_session_data)
    session_data = get_session(sid)
    session_data['session_id'] = sid
    response = actions.session_response(session_data)
    res_json = json.dumps(response)
    return jsonify(res_json), 200

@app.route('/sessions/<session_id>/end', methods=['GET'])
def end_session(session_id):
    #sessions.pop(session_id, None)
    return None, 200

@app.route('/sessions/<session_id>/next', methods=['GET'])
def next(session_id):
    session_data = get_session(session_id)
    print(session_data)
    if not session_data:
        return jsonify({'message': 'Session not found'}), 404
    response = actions.on_next(session_data)
    res_json = json.dumps(response)
    return jsonify(res_json), 200


@app.route('/sessions/<session_id>/select_term', methods=['GET'])
def select(session_id):
    session_data = get_session(session_id)
    if not session_data:
        return jsonify({'message': 'Session not found'}), 404
    term = request.args.get('term')
    if not term:
        return jsonify({'message': 'Specify term query param'}), 400
    return jsonify(actions.on_select_term(session_data, term)), 200