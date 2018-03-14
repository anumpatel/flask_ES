from flask import  Flask, render_template,\
    redirect, session,  url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user,\
    login_required,logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from forms import RegisterForm, LoginForm

from flask_pymongo import PyMongo
from elasticsearch import Elasticsearch, helpers
from bson.json_util import dumps
from bson.objectid import ObjectId
from decouple import config
import certifi

from utils import create_body, build_response_dict

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = config('SQLALCHEMY_URI')
app.config['MONGO_URI'] = config('MONGO_URI')
app.secret_key = config('SECRET_KEY')

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

db = SQLAlchemy(app)
mongo = PyMongo(app)

es = Elasticsearch([config('ELASTIC_URI')], http_auth = (config('ELASTIC_U'), config('ELASTIC_P')), scheme="https", port=443, use_ssl = True, ca_certs=certifi.where())


@login_manager.user_loader
def load_user(username):
    return User.query.filter_by(username = username).first()

class User(db.Model):
    # User model for authentication
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(70), unique = True)
    email = db.Column(db.String(70), unique = True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    password = db.Column(db.String(200))

    def __init__(self, username, email, first_name, last_name, password):
        self.username = username
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.set_pwd(password)
        self.password = self.pw_hash
    
    def __str__(self):
        return '''{0},{1}'''.format(self.first_name,self.last_name)

    def is_active(self):
        return True

    def get_id(self):
        return str(self.username)

    def is_authenticated(self):
        return True

    def set_pwd(self, password):
        self.pw_hash = generate_password_hash(password)
    
    def check_pwd(self, password):
        return check_password_hash(self.password, password)
    

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods = ['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect('/search')

    form = RegisterForm()
    
    if request.method == 'GET':
        return render_template('register.html', form = form)
    

    elif request.method == 'POST':
        if form.validate_on_submit():
            if User.query.filter_by(email = form.email.data).count() > 0:
                return render_template('register.html', error_msg = 'Email address already exists', form = form)
            
            elif User.query.filter_by(username = form.username.data).count() > 0:
                return render_template('register.html', error_msg = 'Username already exists', form = form)
            
            else:

                user_to_add = User(form.username.data, form.email.data, form.f_name.data, form.l_name.data, form.password.data)
                db.session.add(user_to_add)
                db.session.commit()
                login_user(user_to_add)
                return redirect('/search')
        else:
            return render_template('register.html', error_msg = 'Error with the form!', form = form)

    return render_template('register.html')


@app.route('/login', methods = ['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect('/search')

    form = LoginForm()
    if request.method == 'GET':
        return render_template('login.html', form = form)
    elif request.method == 'POST':
        if form.validate_on_submit():
            c_user = User.query.filter_by(username = form.username.data).first()
            if c_user:
                if c_user.check_pwd(form.password.data):
                    login_user(c_user)
                    return render_template('index.html')
                else:
                    return render_template('login.html', form = form, error_msg = 'Incorrect credentials!')
            else:
                    return render_template('login.html', form = form, error_msg = 'Incorrect credentials!')
                
        else:
            return render_template('login.html', form = form, error_msg = 'Validation failed')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return render_template('login.html', form = LoginForm())


@app.route('/search')
@login_required
def search():
    search_string = request.args.get('q')
    explore_id = request.args.get('id')
    if explore_id is not None:
        explore = mongo.db.airports.find({"_id": ObjectId(explore_id)})
        return render_template('raw.html', data = explore)
        

    if search_string is not None:
        if len(search_string) > 0:
            # matching query string with wild-card
            search_string = "*{}*".format(search_string)
            es_result = es.search(index='_all', doc_type='airport', q=search_string, analyze_wildcard = True, size = 1000)
            es_response_dict = build_response_dict(es_result)
            if es_response_dict is None:
                return render_template('search.html', msg = 'No data found!')
            return render_template('search.html', data = es_response_dict)
        else:
            pass

    return render_template('search.html')


if __name__ == '__main__':
    app.run(debug=True)

