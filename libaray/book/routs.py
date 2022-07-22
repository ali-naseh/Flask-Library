import datetime

from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import current_user, login_required
import app
import Models

book = Blueprint('book', __name__)


@login_required
@book.route('/<int:id>')
def single(id):
    stat = False
    user_book = Models.BookInstance.query.filter_by(borrower=current_user.id)
    book = Models.Book.query.get(id)
    for ubook in user_book:
        if ubook.book == book.id:
            stat = True
    return render_template('single.html', book=book, stat=stat)


@login_required
@book.route('/borrow/<int:id>', methods=['get', 'post'])
def borrow(id):
    if request.method == "POST":
        this_book = Models.Book.query.get(id)
        if this_book.quantity != 0:
            book_inst = Models.BookInstance(book=this_book.id, borrower=current_user.id)
            this_book.quantity -= 1
            book_inst.status = 'o'
            app.db.session.add(book_inst)
            app.db.session.commit()
            flash('You Borrowed This Book', 'success')
            return redirect(url_for('book.single', id=this_book.id))
        else:
            flash("There is not any version if this book at this moment", 'warning')
            return redirect(url_for('book.single', id=this_book.id))


@book.route('/search')
def search():
    # page = request.args.get('page', 1, type=int)
    list_books = []
    search_input = request.args.get('s')
    books = Models.Book.query.all()
    for book in books:
        if search_input.lower() in book.title.lower() or search_input.lower() in book.description.lower() or search_input.lower() in book.author.lower():
            list_books.append(book)

    return render_template('book/search.html', books=list_books, search_input=search_input)


@book.route('/categories/<string:name>')
def view_category(name):
    page = request.args.get('page', 1, type=int)
    categ = Models.Category.query.filter_by(name=name).first_or_404()
    books = Models.Book.query.filter_by(category=categ.id).paginate(page=page, per_page=6)
    return render_template('book/categoires.html', books=books, name=name)


@book.route('/returnback/<int:id>', methods=['get', 'post'])
def return_back(id):
    if request.method == "POST":
        Models.BookInstance.query.filter_by(book=id, borrower=current_user.id).delete()
        this_book = Models.Book.query.get(id)
        this_book.quantity += 1
        app.db.session.add(this_book)
        app.db.session.commit()
        flash("Operation Was Successful", 'success')
        return redirect(url_for('book.single', id=this_book.id))


@login_required
@book.route('/reborrow/<int:id>', methods=["get", 'post'])
def reBorrow(id):
    Models.BookInstance.query.filter_by(book=id, borrower=current_user.id).delete()
    lib_book = Models.BookInstance(book=id, borrower=current_user.id)
    app.db.session.add(lib_book)
    app.db.session.commit()
    flash('You ReBorrowed This Book', 'success')
    if current_user.is_admin:
        return redirect(url_for('admin.info'))
    else:
        return redirect(url_for('account.info'))
