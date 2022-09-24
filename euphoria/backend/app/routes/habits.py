from datetime import date

import requests
from flask import Blueprint, current_app, redirect, render_template, request, url_for

from ...common.db.sqlalchemy import session
from ..easy_dates import EasyDate
from ...common.models.habits import Category, CompletedHabit, Habit

blueprint = Blueprint(
    'habits', __name__, template_folder='templates/habits', static_folder='static'
)


@blueprint.route('/', methods=['GET', 'POST'])
def index():
    with session:
        current_habits = session.query(Habit).where(Habit.current.is_(True))
        completed_today = session.query(CompletedHabit).where(
            CompletedHabit.completed_date == date.today()
        )
        not_completed = session.query(Habit).join()

    return render_template(
        'index.html', completed_today=completed_today, not_completed=not_completed
    )


@blueprint.route('/completed/', methods=['GET', 'POST'])
def completed():
    if request.method == 'POST':
        selected_habit = request.form.get('habit')
        date_filter = request.form.get('filter')
    else:
        selected_habit = None
        date_filter = 'this_week'

    with session:
        q = session.query(CompletedHabit)
        q = q.join(Habit, CompletedHabit.habit_id == Habit.id)
        if selected_habit:
            q = q.where(Habit.name == selected_habit)
        first_completed = q.order_by(CompletedHabit.completed_date.asc()).first()
        last_completed = q.order_by(CompletedHabit.completed_date.desc()).first()

        habits = session.query(Habit).all()

    ed = EasyDate()
    filters = {
        'today': (ed.today, ed.tomorrow),
        'yesterday': (ed.yesterday, ed.today),
        'this_week': (ed.week_start, ed.week_end),
        'last_7': (ed.previous_7, ed.today),
        'this_month': (ed.this_month, ed.next_month),
        'last_30': (ed.previous_30, ed.today),
        'this_year': (ed.this_year, ed.next_year),
        'all': (first_completed.complete_date, last_completed.complete_date),
    }

    start_date, end_date = filters.get(date_filter)

    with session:
        q = session.query(CompletedHabit)
        q = q.where(
            CompletedHabit.completed_date >= start_date,
            CompletedHabit.completed_date < end_date,
        )
        completed = q.order_by(CompletedHabit.completed_date.desc()).all()

    return render_template(
        'habits/completed.html',
        habits=habits,
        completed=completed,
        filters=filters,
        date_filter=date_filter,
        long_date=ed.today.strftime('%A %B %d, %Y'),
    )


@blueprint.route('/manage/', methods=['GET', 'POST'])
def manage():
    if request.method == 'POST':
        data = request.form.to_dict()
        method = data.pop('method')
        habit = Habit(**data)

    return render_template('habits/manage.html')


@blueprint.route('/form/', methods=['POST'])
def form():
    api_url = SETTINGS.API_URL
    data = request.form.to_dict()
    method = data.pop('method')
    match method:
        case ['add_habit']:
            habit = Habit(**data)
            requests.post(f'{api_url}/habits', data=habit)
        case ['delete_habit']:
            habit = Habit(**data)
            requests.delete(f'{api_url}/habits/{habit.id}')
        case ['complete_habit']:
            habit = Habit(**data)
            requests.post(f'{api_url}/habits/completed', data=habit)
        case ['add_category']:
            category = Category(**data)
            requests.post(f'{api_url}/habits/categories', data=category)
        case ['delete_category']:
            category = Category(**data)
            requests.delete(f'{api_url}/habits/categories/{category.id}')

    return redirect(url_for('habits.index'))
