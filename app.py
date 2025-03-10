from flask import Flask, redirect, url_for, render_template, request, session, flash, jsonify
from datetime import timedelta, datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'default_secret_key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI', 'sqlite:///default.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.permanent_session_lifetime = timedelta(minutes=5)

db = SQLAlchemy(app)

class users(db.Model):
    ''' Таблица пользователей '''
    _id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    password = db.Column(db.String(200))
    role = db.Column(db.String(15), default="user")

    def __init__(self, name, email, password, role):
        self.name = name
        self.email = email
        self.password = generate_password_hash(password)
        self.role = role

    def check_password(self, password):
        ''' Проверка пароля '''
        return check_password_hash(self.password, password)

class Post(db.Model):
    ''' Таблица для хранения записей пользователей '''
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(500), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('users', backref=db.backref('posts', lazy=True))

    def __init__(self, content, user_id):
        self.content = content
        self.user_id = user_id


with app.app_context():
    ''' Инициализация базы данных '''
    db.create_all()

    admin_name = os.getenv("ADMIN")
    admin_email = os.getenv("ADMIN_EMAIL")
    admin_password = os.getenv("ADMIN_PASSWORD")

    admin_user = users.query.filter_by(name=admin_name).first()
    if not admin_user:
        admin_user = users(name=admin_name, email=admin_email, password=admin_password, role="admin")
        db.session.add(admin_user)
        db.session.commit()


@app.route("/")
def home():
    ''' Домашняя страница '''
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    return render_template("index.html", posts=posts)


@app.route("/register", methods=["POST", "GET"])
def register():
    ''' Эндпоинт для регистрации пользователя '''
    if request.method == "POST":
        username = request.form["nm"]
        email = request.form["email"]
        password = request.form["password"]
        found_user = users.query.filter_by(name=username).first()

        if found_user:
            flash("User already exists!")
            return redirect(url_for("register"))

        new_user = users(name=username, email=email, password=password, role="user")
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful!")
        return redirect(url_for("login"))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Эндпоинт для авторизации"""
    if request.method == "POST":
        user = request.form["nm"]
        password = request.form["password"]
        found_user = users.query.filter_by(name=user).first()

        if found_user and found_user.check_password(password):
            session.permanent = True
            session['user'] = user
            flash("Login successful!")
            return redirect(url_for("home"))  # Перенаправление на домашнюю страницу
        else:
            flash("Invalid username or password")
            return redirect(url_for("login"))

    # Если метод GET, просто отображаем страницу логина
    return render_template("login.html")


@app.route("/text", methods=["POST", "GET"])
def text():
    """Эндпоинт для добавления записи на страницу"""
    if 'user' not in session:
        flash("You need to login first!")
        return redirect(url_for("login"))

    if request.method == "POST":
        content = request.form["content"]
        user = users.query.filter_by(name=session['user']).first()

        if user:
            new_post = Post(content=content, user_id=user._id)
            db.session.add(new_post)
            db.session.commit()
            flash("Post added successfully!")
            return redirect(url_for("home"))

    return render_template("text.html")


@app.route("/logout")
def logout():
    """Эндпоинт для выхода из системы"""
    session.pop('user', None)
    flash("You have been logged out!")
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=False)