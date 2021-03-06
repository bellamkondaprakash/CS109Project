"""
Routes and views for the flask application.
"""


import uuid
from flask import Flask, jsonify, render_template, request
from core.actions import (
    create_session_data, on_next, on_select_term, session_response)

import json

from flask import Flask
app = Flask(__name__)


sessions = {}


def get_session(session_id):
    return sessions.get(session_id, None)


def save_session(session_data):
    sid = str(uuid.uuid4())
    sessions[sid] = session_data
    return sid


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/sessions/<session_id>/new', methods=['POST'])
def new(session_id):
    # remove old session
    sessions.pop(session_id, None)
    _session_data = create_session_data()
    sid = save_session(_session_data)
    session_data = get_session(sid)
    session_data['session_id'] = sid
    response = session_response(session_data)
    res_json = json.dumps(response)
    return res_json, 200

@app.route('/sessions/<session_id>/end', methods=['GET'])
def end_session(session_id):
    sessions.pop(session_id, None)
    return None, 200

@app.route('/sessions/<session_id>/next', methods=['GET'])
def next(session_id):
    session_data = sessions.get(session_id, None)
    if not session_data:
        return jsonify({'message': 'Session not found'}), 404
    return jsonify(on_next(session_data)), 200


@app.route('/sessions/<session_id>/select_term', methods=['GET'])
def select(session_id):
    session_data = get_session(session_id)
    if not session_data:
        return jsonify({'message': 'Session not found'}), 404
    term = request.args.get('term')
    if not term:
        return jsonify({'message': 'Specify term query param'}), 400
    return jsonify(on_select_term(session_data, term)), 200

if __name__ == '__main__':
    app.run(debug=True)
