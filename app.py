import os
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Email
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY','dev-secret')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR,'app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'
admin = Admin(app, name='AdminPanel', template_mode='bootstrap4')

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(120))
    password = db.Column(db.String(255))
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Integer, default=0)

class Lead(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    email = db.Column(db.String(120))
    message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class SecureModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

admin.add_view(SecureModelView(User, db.session))
admin.add_view(SecureModelView(Service, db.session))
admin.add_view(SecureModelView(Lead, db.session))

@login.user_loader
def load_user(uid):
    return User.query.get(int(uid))

class ContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    message = TextAreaField('Message', validators=[DataRequired()])
    submit = SubmitField('Send')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

@app.route('/')
def index():
    services = Service.query.all()
    return render_template('index.html', services=services)

@app.route('/service/<int:sid>')
def service_page(sid):
    s = Service.query.get_or_404(sid)
    return render_template('service.html', service=s)

@app.route('/contact', methods=['GET','POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        l = Lead(name=form.name.data, email=form.email.data, message=form.message.data)
        db.session.add(l)
        db.session.commit()
        flash('Thanks — we will contact you', 'success')
        return redirect(url_for('index'))
    return render_template('contact.html', form=form)

@app.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        u = User.query.filter_by(email=form.email.data).first()
        if u and u.password == form.password.data:
            login_user(u)
            return redirect(url_for('index'))
        flash('Invalid creds', 'danger')
    return render_template('login.html', form=form)

@app.cli.command('create-admin')
def create_admin():
    e = input('email: ')
    n = input('name: ')
    p = input('password: ')
    if User.query.filter_by(email=e).first():
        print('exists')
        return
    u = User(email=e, name=n, password=p, is_admin=True)
    db.session.add(u)
    db.session.commit()
    print('created')

@app.cli.command('seed')
def seed():
    if Service.query.count() == 0:
        s1 = Service(title='Landing Page', description='High converting landing', price=15000)
        s2 = Service(title='Business Site + Admin', description='5 page + admin', price=35000)
        db.session.add_all([s1,s2])
        db.session.commit()
        print('seeded')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
