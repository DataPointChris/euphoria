import requests
from flask import Blueprint, redirect, render_template, request, url_for

from ichrisbirch.config import settings
from ichrisbirch.models.apartments import Apartment, Feature

blueprint = Blueprint(
    'apartments',
    __name__,
    template_folder='templates/apartments',
    static_folder='static',
)


@blueprint.route('/')
def index():
    """Apartments home"""
    apartments = [apt for apt in Apartment.scan()]
    return render_template(
        'apartments.html',
        apartments=apartments,
        apartment=None,
        features=None,
        message='No apartment selected',
    )


@blueprint.route('/<string:name>/')
def apartment(name):
    """Single apartment details"""
    apartments = [apt for apt in Apartment.scan()]
    if apartment := next((apt for apt in apartments if apt.name == name), None):
        features = [Feature(**f) for f in apartment.features]
        message = None
    else:
        features = None
        message = (f'{name} apartment does not exist',)
        return render_template(
            'apartments.html', apartments=apartments, apartment=apartment, features=features, message=message
        )


# transparently redirect to main page
@blueprint.route('/edit/')
def noedit():
    """Redirect from edit page to apartments home"""
    apartments = [apt for apt in Apartment.scan()]
    return render_template(
        'apartments.html', apartments=apartments, apartment=None, features=None, message='No apartment selected'
    )


@blueprint.route('/edit/<string:name>/')
def edit(name):
    """Edit apartment details"""
    apartments = [apt for apt in Apartment.scan()]
    if apartment := next((apt for apt in apartments if apt.name == name), None):
        features = [Feature(**f) for f in apartment.features]
        page = 'edit.html'
        message = None
    else:
        features = None
        page = 'apartments.html'
        message = (f'{name} apartment does not exist',)
    return render_template(page, apartments=apartments, apartment=apartment, features=features, message=message)


@blueprint.route('/form/', methods=['POST'])
def crud():
    """CRUD operations for apartments"""
    api_url = settings.API_URL
    data = request.form.to_dict()
    method = data.pop('method')
    apt = Apartment(**data)
    if method == 'add':
        requests.post(f'{api_url}/tasks', data=apt)
    elif method == 'update':
        requests.put(f'{api_url}//tasks', data=apt)
    elif method == 'delete':
        requests.delete(f'{api_url}//tasks', data=apt)
    return redirect(url_for('apartments.apartment', name=data.get('name')))
