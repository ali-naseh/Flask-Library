import os
import datetime
from flask import Blueprint, render_template, abort, request, flash, redirect, url_for
from flask_login import login_required, current_user
from forms import EditProfileForm, ChangePasswordForm, RegisterForm, AddBookForm, EditBookForm
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
import app
import Models

admin = Blueprint('admin', __name__)


@admin.route('/')
@login_required
def index():
    if not current_user.is_admin:
        abort(403)
    users_books = Models.BookInstance.query.filter_by(borrower=current_user.id)
    books_to_return = []
    for book in users_books:
        stime = datetime.datetime.utcnow() + datetime.timedelta(days=12)
        if stime.date() == book.due_back.date():
            books_to_return.append(book)
        elif datetime.datetime.utcnow().date() > book.due_back.date():
            Models.BookInstance.query.filter_by(book=id, borrower=current_user.id).delete()
            this_book = Models.Book.query.get(id)
            this_book.quantity += 1
            app.db.session.add(this_book)
            app.db.session.commit()
    return render_template('admin/index.html', title='Admin', books_to_return=books_to_return)


@admin.route('/info')
def info():
    if not current_user.is_admin:
        abort(403)

    users_books = Models.BookInstance.query.filter_by(borrower=current_user.id)

    return render_template('admin/info.html', title='Admin - info', borrowedBooks=users_books)


@admin.route('/edit', methods=['get', 'post'])
def edit():
    if not current_user.is_admin:
        abort(403)
    form = EditProfileForm()
    if request.method == "POST":
        if form.validate_on_submit():
            user = Models.User.query.filter_by(email=current_user.email).one()
            user.email = form.email.data
            user.username = form.username.data
            app.db.session.add(user)
            app.db.session.commit()
            flash('Your Profile Updated Successfully', 'success')
            return redirect(url_for('admin.info'))
    return render_template('admin/edit.html', form=form, title='Admin - Edit')


@admin.route('/avatar', methods=['get', 'post'])
def change_avatar():
    if not current_user.is_admin:
        abort(403)
    if request.method == "POST" and 'avatar' in request.files:
        avatar = request.files.get('avatar')
        filename = avatar.filename
        fileSecure = secure_filename(filename)
        if not app.allow_extension(filename):
            flash('Extension is not allowed', 'danger')
            return redirect(url_for('admin.change_avatar'))
        avatar.save(os.path.join(app.app.config['UPLOAD_DIR'], fileSecure))
        user = Models.User.query.filter_by(email=current_user.email).one()
        user.image_file = f'uploads/{filename}'
        app.db.session.add(user)
        app.db.session.commit()
        flash('Avatar Changed Correctly', 'success')
        return redirect(url_for('admin.info'))
    return render_template('admin/avatar.html', title='Admin - Avatar')


@admin.route('/changepassword', methods=['get', 'post'])
def change_password():
    if not current_user.is_admin:
        abort(403)
    form = ChangePasswordForm()
    if request.method == "POST":
        if form.validate_on_submit():
            user = Models.User.query.filter_by(email=current_user.email).first()
            if not user.IsOriginalPassword(password=form.oldPassword.data):
                flash('Password is incorrect', 'warning')
                return redirect(url_for('admin.change_password'))
            user.passwd = form.newPassword.data
            app.db.session.add(user)
            app.db.session.commit()
            flash('Password Changed Successfully', 'success')
            return redirect(url_for('admin.info'))
    return render_template('admin/changepassword.html', form=form, title='Admin - ChangePassword')


@admin.route('/add-book', methods=['get', 'post'])
def add_book():
    form = AddBookForm()
    categories = Models.Category.query.all()
    if request.method == 'POST':
        if form.validate_on_submit():
            name = request.form.get('name')
            description = request.form.get('description')
            category = request.form.get('category')
            author = request.form.get('author')
            quantity = request.form.get('quantity')
            published_at = request.form.get('publish_at')
            published_at = datetime.datetime.strptime(published_at, '%Y-%m-%d')
            thumbnail = form.thumbnail.data
            if thumbnail:
                thumbnail.save(os.path.join(app.app.config['UPLOAD_DIR'], secure_filename(thumbnail.filename)))
            newBook = Models.Book(title=name, description=description, thumbnail=f'uploads/{thumbnail.filename}',
                                  published_at=published_at,
                                  category=category,
                                  author=author,
                                  quantity=quantity)

            app.db.session.add(newBook)
            app.db.session.commit()
            flash("Book has been added successfully", 'success')
            return redirect(url_for('admin.add_book'))
    return render_template('admin/book/addBook.html', form=form, title='Admin - Add Book', categories=categories)


@admin.route('/edit-book', methods=['get', 'post'])
def edit_book():
    form = EditBookForm()
    book = Models.Book.query.get(request.args.get('id'))
    categories = Models.Category.query.all()
    prev_thumb = book.thumbnail
    borrowers = Models.BookInstance.query.filter_by(book=book.id)
    if request.method == "POST":
        if form.validate_on_submit():
            name = request.form.get('name')
            description = request.form.get('description')
            category = request.form.get('category')
            quantity = request.form.get('quantity')
            thumbnail = request.files['thumbnail'] if request.files['thumbnail'] != '' else prev_thumb
            if isinstance(thumbnail, FileStorage):
                filename = secure_filename(thumbnail.filename)
                thumbnail.save(os.path.join(app.app.config['UPLOAD_DIR'], filename))
            book.title = name
            book.description = description
            book.category = category
            book.quantity = quantity
            book.thumbnail = f"uploads/{thumbnail.filename}" if isinstance(thumbnail,
                                                                           FileStorage) else prev_thumb
        app.db.session.add(book)
        app.db.session.commit()
        flash('Book Edited Successfully', 'success')
        return redirect(url_for('admin.get_all_books'))
    return render_template('admin/book/edit.html', form=form, title="Admin - Edit Book", book=book,
                           categories=categories, borrowers=borrowers)


@admin.route('/books', methods=['get', 'post'])
def get_all_books():
    if request.method == "POST":
        Models.Book.query.filter_by(id=request.args.get('id')).delete()
        Models.BookInstance.query.filter_by(book=request.args.get('id')).delete()
        app.db.session.commit()
        return redirect(url_for('admin.get_all_books'))
    on_loan_books = []
    books_ins = Models.BookInstance.query.all()
    books = Models.Book.query.all()
    for b in books:
        for bi in books_ins:
            if b.id == bi.book:
                on_loan_books.append(b.id)
    return render_template('admin/book/list.html', books=books, olb=on_loan_books, title="Admin - Books")


@admin.route('/add-category', methods=['get', 'post'])
def add_category():
    if request.method == 'POST':
        name = request.form.get('name')
        newCat = Models.Category(name=name)
        app.db.session.add(newCat)
        app.db.session.commit()
        flash('Category added', 'success')
        return redirect(url_for('admin.add_category'))
    return render_template('admin/category/addCategory.html', title="Admin - Add Category")


@admin.route('/add-user', methods=['get', 'post'])
def add_user():
    form = RegisterForm()
    if request.method == "POST":
        if form.validate_on_submit():
            newUser = Models.User(username=form.username.data, email=form.email.data, passwd=form.password.data)
            app.db.session.add(newUser)
            app.db.session.commit()
            flash(f'{form.username.data} Has Been Registered Successfully', 'success')
            return redirect(url_for('admin.index'))
    return render_template("admin/user/addUser.html", form=form, title="Admin - Add User")


@admin.route('/users', methods=['get', 'post'])
def get_all_users():
    if request.method == "POST":
        Models.User.query.filter_by(id=request.args.get('id')).delete()
        Models.BookInstance.query.filter_by(borrower=request.args.get('id')).delete()
        app.db.session.commit()
        return redirect(url_for('admin.get_all_users'))
    users = Models.User.query.all()
    return render_template('admin/user/list.html', users=users, title="Admin - Users")


@admin.route('/edit-user', methods=['get', 'post'])
def edit_user():
    form = EditProfileForm()
    user_id = request.args.get('id')
    user = app.db.session.query(Models.User).get(user_id)
    user_books = Models.BookInstance.query.filter_by(borrower=user.id)
    books = Models.Book.query.all()
    book = []
    for ub in user_books:
        for b in books:
            if ub.book == b.id:
                book.append(b)
    if request.method == "POST":
        if form.validate_on_submit():
            user.username = form.username.data
            user.email = form.email.data
            app.db.session.add(user)
            app.db.session.commit()
            flash(f'{user.username} edited successfully', 'success')
            return redirect(url_for('admin.get_all_users'))
    return render_template('admin/user/edit.html', form=form, titel="Admin - Edit User", user=user,
                           borrowedBooks=user_books, book=book)
