from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app import db
from app.user import bp
from app.user.forms import EditProfileForm
from app.models import User, Destination


@bp.route('/dashboard/<page>', methods=['GET', 'POST'])
@login_required
def dashboard(page):
    if page == "settings":
        form = EditProfileForm()
        if form.validate_on_submit():
            current_user.displayname = form.displayname.data
            current_user.location = form.location.data
            current_user.bio = form.bio.data
            db.session.commit()
            flash('Your settings have been saved.')
            return redirect(url_for('user.dashboard', page='settings'))
        elif request.method == 'GET':
            form.displayname.data = current_user.displayname
            form.location.data = current_user.location
            form.bio.data = current_user.bio
        return render_template('user/dashboard.html', page=page, form=form)
    return render_template('user/dashboard.html', page=page)


@bp.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    destinations = Destination.query.filter_by(user_id=user.id)
    return render_template('user/user_profile.html', user=user, destinations=destinations)
