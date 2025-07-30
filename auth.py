from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, current_user
from models.models import User, Admin, db

auth_blueprint = Blueprint('auth', __name__)

@auth_blueprint.route('/', methods=['GET', 'POST'])
@auth_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        
        # Try admin first
        admin = Admin.query.filter_by(username=username).first()
        if admin and admin.check_password(password):
            login_user(admin)
            flash(f"Welcome Admin {username}!")
            return redirect(url_for('admin.dashboard'))
        
        # Try regular user
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            flash(f"Welcome {username}!")
            return redirect(url_for('user.dashboard'))
        
        flash("Invalid username or password!")
    
    return render_template("login.html")

@auth_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        
        # Check if username already exists (in either table)
        if (User.query.filter_by(username=username).first() or 
            Admin.query.filter_by(username=username).first()):
            flash("Username already taken.")
            return redirect(url_for('.register'))
        
        # Create new user (NOT admin)
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash("Registration successful! Please login.")
        return redirect(url_for('.login'))
    
    return render_template("register.html")

@auth_blueprint.route('/logout')
def logout():
    logout_user()
    flash("Logged out successfully.")
    return redirect(url_for('.login'))
