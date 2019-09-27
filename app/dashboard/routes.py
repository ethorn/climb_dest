from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app import db
from app.dashboard import bp
from app.dashboard.forms import EditProfileForm


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
            return redirect(url_for('dashboard.dashboard', page='settings'))
        elif request.method == 'GET':
            form.displayname.data = current_user.displayname
            form.location.data = current_user.location
            form.bio.data = current_user.bio
        return render_template('dashboard/dashboard.html', page=page, form=form)
    return render_template('dashboard/dashboard.html', page=page)
