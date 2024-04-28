import json
import logging
import re

import httpx
import pendulum
from flask import Blueprint, redirect, render_template, request, url_for

from ichrisbirch.app.helpers import handle_if_not_response_code
from ichrisbirch.config import get_settings

settings = get_settings()

blueprint = Blueprint('home', __name__, template_folder='templates', static_folder='static')

logger = logging.getLogger(__name__)


@blueprint.route('/', methods=['GET'])
def index():
    return render_template('index.html', settings=settings)


@blueprint.route('/server-stats/')
def server_stats():
    return render_template(
        'server-stats.html',
        settings=settings,
        server_time=pendulum.now('UTC').isoformat(),
        local_time=pendulum.now().isoformat(),
    )


@blueprint.route('/issue/', methods=['GET', 'POST'])
def issue():
    if request.method == 'GET':
        return redirect(url_for('home.index'))

    issue = request.form.to_dict()
    labels = [k for k, v in issue.items() if v == 'on']
    logger.debug(f'Issue submitted from page: {request.referrer}')
    logger.debug(f'Issue details: {issue}')
    body_template = f'''
        {issue['description']}


        ---
        ### Autogenerated Details

        **User-Agent:**
        {'\n'.join([f'\t - {part})' for part in re.split(r'\)', request.headers.get('User-Agent', '')) if part])}

        **Referer:** {request.headers.get('Referer')}

        **Address:** {request.headers.get('X-Forwarded-For', request.remote_addr)}
    '''
    dedented = '\n'.join(line.strip() for line in body_template.split('\n'))
    data = json.dumps({'title': issue['title'], 'body': dedented, 'labels': labels})
    response = httpx.post(settings.github.api_url_issues, content=data, headers=settings.github.api_headers)
    handle_if_not_response_code(201, response, logger)

    return redirect(request.referrer or url_for('home.index'))
