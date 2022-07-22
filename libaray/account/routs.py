import os
import datetime
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from forms import EditProfileForm, ChangePasswordForm
from werkzeug.utils import secure_filename
import app
import Models

account = Blueprint('account', __name__)


@account.route('/')
@login_required
def index():
    users_books = Models.BookInstance.query.filter_by(borrower=current_user.id)
    books_to_return = []
    for book in users_books:
        stime = datetime.datetime.utcnow() + datetime.timedelta(days=2)
        if stime.date() == book.due_back.date():
            books_to_return.append(book)
        elif datetime.datetime.utcnow().date() > book.due_back.date():
            Models.BookInstance.query.filter_by(book=id, borrower=current_user.id).delete()
            this_book = Models.Book.query.get(id)
            this_book.quantity += 1
            app.db.session.add(this_book)
            app.db.session.commit()
    return render_template('account/index.html', title='Account', books_to_return=books_to_return)


@account.route('/info')
def info():
    users_books = Models.BookInstance.query.filter_by(borrower=current_user.id)
    return render_template('account/info.html', title='Account - info', borrowedBooks=users_books)


@account.route('/edit', methods=['get', 'post'])
def edit():
    form = EditProfileForm()
    if request.method == "POST":
        if form.validate():
            user = Models.User.query.filter_by(email=current_user.email).first()
            user.email = form.email.data
            user.username = form.username.data
            app.db.session.add(user)
            app.db.session.commit()
            flash('Your Profile Updated Successfully', 'success')
            return redirect(url_for('account.info'))
    return render_template('account/edit.html', form=form, title='Account - Edit')


@account.route('/avatar', methods=['get', 'post'])
def change_avatar():
    if request.method == 'POST' and 'avatar' in request.files:
        avatar = request.files.get('avatar')
        filename = avatar.filename
        fileSecure = secure_filename(filename)
        if not app.allow_extension(filename):
            flash('Extension is not allowed', 'danger')
            return redirect(url_for('account.change_avatar'))
        avatar.save(os.path.join(app.app.config['UPLOAD_DIR'], fileSecure))
        user = Models.User.query.filter_by(email=current_user.email).one()
        user.image_file = f'uploads/{filename}'
        app.db.session.add(user)
        app.db.session.commit()
        flash('Avatar Changed Correctly', 'success')
        return redirect(url_for('account.info'))
    return render_template('account/avatar.html', title='Account - Avatar')


@account.route('/changepassword', methods=['get', 'post'])
def change_password():
    form = ChangePasswordForm()
    if request.method == "POST":
        if form.validate_on_submit():
            user = Models.User.query.filter_by(email=current_user.email).one()
            if not user.IsOriginalPassword(form.oldPassword.data):
                flash('Password is incorrect', 'warning')
                return redirect(url_for('account.change_password'))
            user.passwd = form.newPassword.data
            app.db.session.add(user)
            app.db.session.commit()
            flash('Password Changed Successfully', 'success')
            return redirect(url_for('account.info'))
    return render_template('account/changepassword.html', form=form, title='Account - ChangePassword')
