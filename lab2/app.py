from flask import Flask, render_template, url_for, redirect
from flask import request, session # routing data through pages without calling db everytime
from flask import flash
from flask_sqlalchemy import SQLAlchemy # database
from flask_login import login_user, logout_user, login_required, LoginManager, UserMixin, current_user # authentication, authorization: rule(user, admin)
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta

## Authentication steps:
### 1- login_manger = LoginManager(app) # configuration login manger
### 2- at model class Model(UserMixin, db.Model)
### 3- function get user it's self (def login_data(id): return User.query.get(int(id))) => call every time i go from route to another route
### 4- login_user(user_data_from_db), logout_user()

## Authorization steps:
### 1- Modify Model (rule)
### 2- Migrates of db:
# a)flask db init => only once bcz it creates migration folder
# b)flask db migrate -m "modifes schema"
# c)flask db upgrade/downupgrade
### 3- Make Decorator for the rule

from functools import wraps
def rule_required(rule):
    def decorator(f):
        def decorated_function(*args, **kwargs):
            if not(current_user.is_authenticated) or current_user.rule != rule:
                return render_template("errors/unauthorized.html")
            return f(*args, **kwargs)
        return decorated_function
    return decorator

app = Flask(__name__)
app.secret_key = "Ahmed123" # session key
app.permanent_session_lifetime = timedelta(seconds=30) # session_lifetime

## step-1
# http://127.0.0.1:5000/students
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///project.db'
db = SQLAlchemy(app)
login_manger = LoginManager()
login_manger.init_app(app)
migrate = Migrate(db=db, app=app)
# app['SERCRET_KEY'] = ""

## step-2
### Model
class User(UserMixin, db.Model):
    #  __tablename__ = "users"
     # static attributes {schema of db}
     id = db.Column('id', db.Integer, primary_key=True)
     username = db.Column(db.String(50), unique=True)
     password = db.Column(db.String(50), nullable=False)
     rule = db.Column(db.String, nullable=False)

     def __init__(self, username, password, rule):
         self.username = username
         self.password = password
         self.rule = rule

class Book(db.Model):
    id = db.Column('id', db.Integer,primary_key=True)
    title = db.Column(db.String(50),nullable=False)
    author = db.Column(db.String(20),nullable=False)
    def __init__(self,title,author):
        self.title=title
        self.author=author
        
# BOoks routes
@app.route("/book/del/<int:id>", methods=['DELETE','GET'],endpoint='book.del')
def del_book(id):
    book=Book.query.filter_by(id=id).first()
    print(book)
    db.session.delete(book)
    db.session.commit()
    return redirect (url_for("all_books"))

@app.route("/book", methods=['GET', 'POST'],endpoint='book.add')
@rule_required('admin')
def add_book():
    if request.method == 'POST':
        book_title = request.form['bt']
        book_author = request.form['ba']
        book = Book(book_title,book_author)
        db.session.add(book)
        db.session.commit()
        return redirect (url_for("all_books"))
    else:
        return render_template("books/addbook.html")

        

@app.route("/books")
def all_books():
    books=Book.query.all()
    return render_template("books/books.html", books=books)

@app.route("/home")
@app.route("/")
def home_page():
    return render_template("home.html")

# def login_page():
#     return render_template("login.html")

# app.add_url_rule("/login", view_func=login_page)

## http methods [GET, POST]
@app.route("/signup", methods=['GET', 'POST'])
def sign_up():
    if request.method == "POST": # POST
        user_name = request.form['nm']
        password = request.form['ps']
        confirm_password = request.form['confirm_ps']
        # validate confirm == password
        if password == confirm_password:
            # validate db
            found_user = User.query.filter_by(username=user_name).first() # if found User, else None 
            if found_user: # already exsist b4
                flash("User ALready Exsist")
                return render_template("users/signup.html")
            else: # save account
                hashed_password = generate_password_hash(password)
                u1 = User(user_name, hashed_password, 'user')
                db.session.add(u1)
                db.session.commit()

                # db.session.delete(u1)
                # db.session.commit()

                # u1.username = 'Ziad'
                # db.session.commit()

                # User.query.filter_by(username='Ahmed') # equality only
                # User.query.filter(User.username) # where
                
                # SELECT, FROM, WHERE, GROUP_BY, HAVING, ORDER_BY, LIMIT
                # from sqlalchemy import func, and_, or_, not_
                # users_result = User.query.with_entities(User.username, func.count(User.id)).filter(User.id > 0).group_by(User.username).having(func.count(User.id) >= 1).order_by(func.count(User.id).desc()).limit(3).all()
                # # users_result = User.query.with_entities(User.id, func.count(User.username)).filter(and_(User.id > 0, User.username=='Ahmed')).group_by(User.id).having(func.count(User.username) >= 1).order_by(func.count(User.username).desc()).limit(3).all()
                # print(users_result)
                return redirect (url_for("login"))
            
        else:
            flash("confirm password and password doesnt match")
            return render_template("users/signup.html")
    else: # GET
        return render_template("users/signup.html") # users/signup.html

@app.route("/login", methods=['GET', 'POST']) 
def login():
    if request.method == "GET": # GET
        if 'username' in session.keys():
            flash("Already Logined", "info")
            return redirect(url_for('user.profile'))
        else:
            flash("Please Type username and password", "info")
            return render_template("login.html", images=['images_3.png', 'images_4.png'])
    else: # POST
        user_name = request.form['nm']
        password = request.form['ps']
        # vliadate db
        user_found = User.query.filter_by(username=user_name).first() # if not None
        if user_found:
            if user_found.rule == "admin":
                if user_found.password == password:
                    # session
                    session['username'] = user_name
                    session['password'] = user_found.password
                    session.permanent = True # to reopen borwser and session is saved their
                    flash("Successfully login", "info")
                    login_user(user_found) # user_instance of db
                    return redirect(url_for('users.index'))
                else:
                    flash("Incorrect Password", 'info')
                    return render_template("login.html")
            elif check_password_hash(user_found.password, password):
                # session
                session['username'] = user_name
                session['password'] = user_found.password
                session.permanent = True # to reopen borwser and session is saved their
                flash("Successfully login", "info")
                login_user(user_found) # user_instance of db
                return redirect(url_for('user.profile'))
            else:
                flash("Incorrect Password", 'info')
                return render_template("login.html")
        else:
            flash("Account Doesn't Exsist", 'info')
            return redirect(url_for("sign_up"))

@app.route("/profile", endpoint='user.profile')
@rule_required('user')
def show_profile():
    if 'username' in session.keys():
        name = session['username']
        password = session['password']
        return render_template("profile.html", name=name, password=password)
    
@app.route("/users", endpoint='users.index')
@rule_required('admin')
def get_all_users():
    users = User.query.all()
    return render_template("users/users.html", users=users)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    if 'username' in session.keys():
        session.pop('username')
        session.pop('password')
    return redirect(url_for("home_page"))

@login_manger.user_loader # load user each time you change your route
def login_data(id):
    return User.query.get(id)
  
@app.errorhandler(404)
def error(error):
    return render_template('errors/error.html')

with app.app_context(): # operations that are tied to your app
    db.create_all() # to create tables
    
if __name__ == "__main__":
    app.run(debug=True, port=5000)