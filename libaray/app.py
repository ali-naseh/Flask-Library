import os
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, redirect, request, url_for, flash
from forms import LoginForm, RegisterForm
from flask_login import LoginManager, login_user, logout_user, current_user
from flask_moment import Moment

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'YOUR SECRET KEY'
app.config['UPLOAD_DIR'] = os.path.curdir + "/static/uploads/"

db = SQLAlchemy(app)
moment = Moment(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'warning'

import Models
from account.routs import account
from admin.routs import admin
from book.routs import book

app.register_blueprint(account, url_prefix='/account')
app.register_blueprint(admin, url_prefix='/admin')
app.register_blueprint(book, url_prefix='/book')


def allow_extension(filename):
    ext = filename[-3:]
    extensions = {'png', 'jpg'}
    if ext not in extensions:
        return False
    return True


@login_manager.user_loader
def userLoader(user_id):
    return Models.User.query.get(user_id)


@app.route('/')
def home():
    page = request.args.get('page', 1, type=int)
    books = Models.Book.query.order_by(Models.Book.published_at.desc()).paginate(page=page, per_page=6)
    categories = db.session.query(Models.Category).all()
    return render_template('home.html', books=books, categories=categories)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if request.method == "POST":
        if form.validate_on_submit():
            user = Models.User.query.filter_by(email=form.email.data).first()
            if not user:
                flash('User Does Not Exist', 'warning')
                return redirect(url_for('login'))
            if user and user.IsOriginalPassword(form.password.data):
                login_user(user)
                next_page = request.args.get('next')
                flash('You Logged In Successfully', 'success')
                return redirect(next_page) if next_page else redirect(url_for('home'))
    return render_template('auth/login.html', form=form, title='Log In')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if request.method == "POST":
        if form.validate_on_submit():
            newUser = Models.User(username=form.username.data, email=form.email.data, passwd=form.password.data)
            db.session.add(newUser)
            db.session.commit()
            flash('You Have Been Registered Successfully', 'success')
            return redirect(url_for('login'))
    return render_template('auth/register.html', form=form, title="Register")


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.template_filter('subContent')
def subContent(content):
    return content[:50] + " ... "


app.jinja_env.filters['subContent'] = subContent

if __name__ == '__main__':
    app.run(debug=True)
