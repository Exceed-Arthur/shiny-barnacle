import flask_login
from flask import Blueprint, render_template, request, flash, redirect, url_for
import server_funcs
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()
from flask_login import login_user, login_required, logout_user, current_user
from random import randrange
import email_funcs

auth = Blueprint('auth', __name__)
email = ''
password1 = ''
password2 = ''
six_digit_code = ''


@auth.route('/Login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['submit-both'] == 'login':
            email = request.form.get('email')
            password = request.form.get('password')
            user = User.query.filter_by(email=email).first()
            if user:
                if check_password_hash(user.password, password):
                    flash('Logged in successfully!', category='success')
                    login_user(user, remember=True)
                    return redirect(url_for('views.home'))
                else:
                    flash('Incorrect password, try again.', category='error')
            else:
                flash('Email does not exist.', category='error')
        elif request.form['submit-both'] == 'forgot':
            return redirect(url_for('auth.forgot'))
        elif request.form['submit-both'] == 'Sign Up':
            return redirect(url_for('auth.sign_up'))
    return render_template("login.html", user=current_user)


@auth.route('/Recover', methods=['GET', 'POST'])
def forgot():
    if request.method == 'POST':
        if request.form['submit-both'] == 'get_password':
            email1 = request.form.get('email')
            if server_funcs.user_exists(email1):
                email_funcs.itoven_send_email_str(email1, subject="Secure Password Request - iToven AI", message=server_funcs.get_platypus(username=email1))
                flash("Check your email to re-gain account access, then log back in. Check all email folders if not in main inbox, and give it at least 30 seconds to finish sending.")
                redirect(url_for('auth.login'))
            else:
                flash('Email does not exist.', category='error')
        if request.form['submit-both'] == 'redirecter-portal':
            return redirect(url_for('views.home'))
        elif request.form['submit-both'] == 'redirecter-landing':
            return redirect(url_for('views.account_page'))
    return render_template("forgot_password.html", user=current_user)


@auth.route('/Logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/Register', methods=['GET', 'POST'])
def sign_up():
    global email
    global password1
    global password2
    global six_digit_code
    if request.method == 'POST':
        if request.form['submit-both'] == 'submit-email':
            six_digit_code = []
            email = request.form.get('email')
            password1 = request.form.get('password1')
            password2 = request.form.get('password2')
            user = User.query.filter_by(email=email).first()
            if user:
                flash('Email already exists.', category='error')
            elif email in server_funcs.txt_file_to_listv2('/static/bad_emails.txt'):
                flash('Sneaky! We worked too hard on this project to allow disposable emails. Try a safer email provider.')
            elif len(email) < 4:
                flash('Email must be greater than 3 characters.', category='error')
            elif password1 != password2:
                flash('Passwords don\'t match.', category='error')
            elif len(password1) < 7:
                flash('Password must be at least 7 characters.', category='error')
            else:
                for i in range(6):
                    six_digit_code.append(str(randrange(9)))
                six_digit_code = str(six_digit_code).replace("'", '')
                six_digit_code = six_digit_code.replace("]", '')
                six_digit_code = six_digit_code.replace("[", '')
                six_digit_code = six_digit_code.replace(" ", '')
                six_digit_code = six_digit_code.replace(",", "")
                print(six_digit_code)
                try:
                    email_funcs.itoven_send_email_str(to=email, subject='iToven AI - Your Verification Code',
                                                      message=f"Hello from Arthur (founder of iToven AI and Exceed IO)! Thank you for checking out our service.\n Your code is; {six_digit_code}")
                except:
                    flash("Try again. Server either didn't approve your email or is unresponsive.")
                flash(message='Great work! Please check your email for the confirmation code to continue.')
        if request.form['submit-both'] == 'submit-verification':
            print(f"test?{six_digit_code}")
            code_user = request.form.get('verification')
            if code_user == six_digit_code:
                new_user = User(email=email, password=generate_password_hash(
                    password1, method='sha256'))
                db.session.add(new_user)
                db.session.commit()
                login_user(new_user, remember=True)
                server_funcs.create_dyno_acct(username=flask_login.current_user.email, platypus=password1)
                flash('Account created!', category='success')
                return redirect(url_for('views.home'))
            else:
                flash(
                    "Error. Invalid code. If you would, just refresh this page. We can start this process over no problem!")
    return render_template("sign_up.html", user=current_user)
