import logging

from fastapi import status
from flask import Blueprint
from flask import abort
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for
from flask_login import current_user
from flask_login import login_required
from flask_login import login_user
from flask_login import logout_user

from ichrisbirch import models
from ichrisbirch import schemas
from ichrisbirch.app.forms.auth import LoginForm
from ichrisbirch.app.forms.auth import SignupForm
from ichrisbirch.app.query_api import QueryAPI
from ichrisbirch.app.utils import http as http_utils

logger = logging.getLogger('app.auth')
blueprint = Blueprint('auth', __name__, template_folder='templates/auth', static_folder='static')
users_api = QueryAPI(base_url='users', api_key='', logger=logger, response_model=schemas.User)


@blueprint.route('/login/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(request.referrer or url_for('users.profile'))
    if request.method == 'GET':
        session['next'] = request.args.get('next')
    form = LoginForm()
    if form.validate_on_submit():
        user = users_api.get_one(['email', form.email.data])
        user = models.User(**user.model_dump())
        if user and user.check_password(password=form.password.data):
            login_user(user, remember=form.remember_me.data)
            logger.debug(f'logged in user: {user.name} - last login: {user.last_login}')
            next_page = session.pop('next', url_for('users.profile'))
            logger.debug(f'login will redirect to: {next_page}')

            if not http_utils.url_has_allowed_host_and_scheme(next_page, request.host):
                return abort(status.HTTP_401_UNAUTHORIZED, f'Unauthorized URL: {next_page}')

            return redirect(next_page or url_for('users.profile'))

        flash('Invalid username/password combination')
        return redirect(url_for('auth.login'))

    return render_template('auth/login.html', form=form, template='login-page')


@blueprint.route('/signup/', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        logger.debug('signup form validated')
        if not (existing_user := users_api.get_one(['email', form.email.data])):
            logger.info(f'creating a new user with email: {form.email.data}')
            data = {'name': form.name.data, 'email': form.email.data, 'password': form.password.data}
            new_user = users_api.post(data=data)
            new_user = models.User(**new_user.model_dump())
            login_user(new_user)
            return redirect(url_for('users.profile'))
        logger.warning(f'duplicate email registration: {form.email.data}')
        logger.info(f'last login: {existing_user.last_login}')
        flash('A user already exists with that email address.')

    return render_template(
        'auth/signup.html',
        title='Create an Account.',
        form=form,
        template='signup-page',
        body="Sign up for a user account.",
    )


@blueprint.route('/logout/')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home.index'))
