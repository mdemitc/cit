from flask import redirect, render_template, request, make_response, g
from flask import Blueprint, session, jsonify

import authomatic
from authomatic.adapters import WerkzeugAdapter
from authomatic import Authomatic

from .models import User
from ..db import db

auth_bp = Blueprint('auth', __name__)

def _session_saver():
    session.modified = True

@auth_bp.route('/login/fb/', methods=['GET', 'POST'])
def login():
    response = make_response()
    result = g.authomatic.login(WerkzeugAdapter(request, response), 'fb',
                                session=session,
                                session_saver=_session_saver)
    if result:
        if result.user:
            result.user.update()
            user = User.query.filter_by(fb_id = result.user.id).first()
            if not user:
                db.create_all()
                db.session.add(User(result.user.first_name, result.user.last_name, result.user.id, result.user.email))
                db.session.commit()
                user = User.query.filter_by(fb_id = result.user.id).first()
            session['user_id'] = user.id
            return redirect('/')

        elif result.error:
            raise Exception('FB login failed.')
    return response

@auth_bp.route('/user-info/', methods=['GET'])
def user_info():
    res = {}
    if g.user:
        res = ({'id': g.user.id, 'first_name': g.user.fb_first_name, 'last_name': g.user.fb_last_name, 'fb_id': g.user.fb_id, 'email': g.user.email})
    return jsonify(res)
