import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db
from sqlalchemy_utils.types.choice import ChoiceType


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120))
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(80))
    is_admin = db.Column(db.Boolean(), default=False)
    image_file = db.Column(db.String(120), default='')
    time_created = db.Column(db.DateTime(), default=datetime.datetime.utcnow())

    @property
    def passwd(self):
        raise AttributeError("Access Forbidden")

    @passwd.setter
    def passwd(self, password):
        self.password = generate_password_hash(password)

    def IsOriginalPassword(self, password):
        return check_password_hash(self.password, password)


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), unique=True)
    category = db.Column(db.Integer, db.ForeignKey('category.id'))
    description = db.Column(db.Text)
    author = db.Column(db.String(150), default='No Info')
    quantity = db.Column(db.Integer, default=1)
    published_at = db.Column(db.DateTime(), default=datetime.datetime.utcnow())
    thumbnail = db.Column(db.String(120), default='')

    def get_category(self):
        category = Category.query.get(self.category)
        return category.name


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))


class BookInstance(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    book = db.Column(db.Integer, db.ForeignKey('book.id'))
    borrower = db.Column(db.Integer, db.ForeignKey('user.id'))
    due_back = db.Column(db.DateTime(),
                         default=datetime.datetime.utcnow() + datetime.timedelta(days=15))
    LOAN_STATUS = [
        ('o', 'On loan'),
        ('a', 'Available')
    ]
    status = db.Column(ChoiceType(LOAN_STATUS, impl=db.String()), max_length=1, default='a')

    def get_book(self):
        book = Book.query.get(self.book)
        return book

    def get_borrower(self):
        user = User.query.get(self.borrower)
        return user
