from urllib.parse import quote
import flask_login
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_user, login_required, logout_user, current_user
from urllib3.packages.six import wraps
import os
import server_functions
from website.models import User
import server_funcs
from website.models import Note
from website import db
import json
views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        if request.form['home-redirecters'] == 'redirecter-download':
            return redirect(url_for('views.download_page'))
        elif request.form['home-redirecters'] == 'redirecter-account':
            return redirect(url_for('views.account_page'))
        elif request.form['home-redirecters'] == 'redirecter-membership':
            return redirect(url_for('views.membership_page'))

    return render_template("home.html", user=current_user)


@views.route('/Download', methods=['GET', 'POST'])
def download_page():
    if request.method == 'POST':
        if request.form['home-redirecters'] == 'redirecter-portal':
            return redirect(url_for('views.home'))
        elif request.form['home-redirecters'] == 'redirecter-landing':
            return redirect(url_for('views.account_page'))
        elif request.form['home-redirecters'] == 'pc_download':
            return redirect(url_for('views.download_pc'))
        elif request.form['home-redirecters'] == 'mac_download':
            return redirect(url_for('views.download_mac'))
    return render_template("download_page.html", user=current_user)


@views.route('/Account', methods=['GET', 'POST'])
def account_page():
    username = flask_login.current_user.email
    favorites_count = len(server_funcs.get_favorites_list_user(username))
    if favorites_count == ("None" or None):
        favorites_count = 0
    membership_status = server_funcs.get_membership_status_user(username)
    credits_count = server_funcs.get_user_credit_count(username)
    if request.method == 'POST':
        if request.form['home-redirecters'] == 'redirecter-portal':
            return redirect(url_for('views.home'))
        elif request.form['home-redirecters'] == 'redirecter-landing':
            return redirect(url_for('views.account_page'))
    return render_template("account_page.html", user=current_user, username=username, credits_count=credits_count,
                           favorites_count=favorites_count, membership_status=membership_status)


@views.route('/Pro', methods=['GET', 'POST'])
def membership_page():
    membership_status = server_funcs.get_membership_status_user(flask_login.current_user.email)
    if membership_status not in ["Gold", "Silver"]:
        membership_status = "Free"
    if request.method == 'POST':
        if request.form['home-redirecters'] == 'silver':
            if membership_status.lower() == 'silver':
                flash("You already have a silver membership!")
            else:
                return redirect(url_for('views.activate_silver'))
        elif request.form['home-redirecters'] == 'gold':
            if membership_status.lower() == 'gold':
                flash(
                    'You are already a gold-member. Manage your account in the user portal or use it in the desktop app.')
            else:
                return redirect(url_for('views.activate_gold'))
        elif request.form['home-redirecters'] == 'cancel':
            if membership_status.lower() == 'free':
                flash('You are a free member. Nothing to cancel.')
            else:
                return redirect(url_for('views.cancel'))
        elif request.form['home-redirecters'] == 'upgrade':
            if membership_status.lower() == 'gold':
                flash(
                    'You already have a gold membership. Manage your account in the user portal or use it in the desktop app.')
            else:
                return redirect(url_for('views.activate_gold'))
        elif request.form['home-redirecters'] == 'redirecter-portal':
            return redirect(url_for('views.home'))
        elif request.form['home-redirecters'] == 'redirecter-landing':
            return redirect(url_for('views.account_page'))
    return render_template("membership_page.html", user=current_user, membership_status=membership_status)


@login_required
@views.route("/DownloadingForPC")
def download_pc():
    if not os.name == 'nt':
        flash('You are using a Mac. Please download the Mac version.')
        return redirect(url_for('views.download_page'))
    else:
        flash('Downloading PC Install Wizard!')
        <a href='build_dists/iToven Sounds-Musical AI Setup.exe'> </a>
        if request.method == 'POST':
            if request.form['home-redirecters'] == 'redirecter-portal':
                return redirect(url_for('views.home'))
            elif request.form['home-redirecters'] == 'redirecter-landing':
                return redirect(url_for('views.account_page'))
            elif request.form['home-redirecters'] == 'redirecter-account':
                return redirect(url_for('views.account_page'))
    return render_template('download_success_pc.html', user=current_user)


@login_required
@views.route("/DownloadingForMac")
def download_mac():
    if not os.name == 'nt':
        flash('Downloading Mac Install Wizard')
        <a href='build_dists/iToven Sounds - Musical AI Setup.zip'> </a>
        if request.method == 'POST':
            if request.form['home-redirecters'] == 'redirecter-portal':
                return redirect(url_for('views.home'))
            elif request.form['home-redirecters'] == 'redirecter-landing':
                return redirect(url_for('views.account_page'))
            elif request.form['home-redirecters'] == 'redirecter-account':
                return redirect(url_for('views.account_page'))
    else:
        flash('You are using a PC. This is the Mac Version. Please download the PC version.')
        return redirect(url_for('views.download_page'))
    return render_template('download_success_mac.html', user=current_user)


@login_required
@views.route(
    '/ExecuteSilver?00D0OD%OO8OO@!ii1IILIliIED36D807974A9BDA7Bi1230589ufyc??fculknig0154aq35115asfasfasfaq3219196349578D662C29BA9FAB14EFA55DF7341F8E3F6B5E01C572EB467DEB14CD08DC5D2F332991EF1CAE5DCC11AB422EC6A1E2AC1B268A6us6er?83381li02oiH8B9F68BD4BD1F9B5572F2D379128D062468C847DA4F9C2B379081F409A2589DA',
    methods=['POST', 'GET'])
def buy_silver():
    server_funcs.activate_subscription(flask_login.current_user.email, 'Silver')
    if request.method == 'POST':
        if request.form['home-redirecters'] == 'redirecter-portal':
            return redirect(url_for('views.home'))
        elif request.form['home-redirecters'] == 'redirecter-landing':
            return redirect(url_for('views.account_page'))
        elif request.form['home-redirecters'] == 'redirecter-account':
            return redirect(url_for('views.account_page'))
    return render_template('execute_silver.html', user=current_user)


def you_sure():
    return "Are you sure?"


@login_required
@views.route(
    '/ExecuteGold?DE67000101010D0OD%OO8OO@!ii1IILIliIED36D807974A9BDA7Bi1230589ufyc??fculknig0154aq35115asfasfasfaq3219196349578D662C29BA010000010100101@932EE9B187E0048830A48F0134D5E217F1CDCA208D8797DC0D36825E6BB6DD00OLJLjlijOD%OO81liLLl?!%$%OO8083O543240OC943F91illiC5CAOD0B8FCB87C530DlI1@!0OO6C08BE0',
    methods=['POST', 'GET'])
def buy_gold():
    server_funcs.activate_subscription(flask_login.current_user.email, 'Gold')
    if request.method == 'POST':
        if request.form['home-redirecters'] == 'redirecter-portal':
            return redirect(url_for('views.home'))
        elif request.form['home-redirecters'] == 'redirecter-landing':
            return redirect(url_for('views.account_page'))
        elif request.form['home-redirecters'] == 'redirecter-account':
            return redirect(url_for('views.account_page'))
    return render_template('execute_gold.html', user=current_user)


@views.route('/Support', methods=['POST', 'GET'])
def support():
    if request.method == 'POST':
        if request.form['home-redirecters'] == 'redirecter-account':
            return redirect(url_for('views.home'))
    return render_template('support_page.html', user=current_user)


@views.route('/Silver', methods=['POST', 'GET'])
def activate_silver():
    return render_template('activate_silver.html', user=current_user)


@views.route('/Gold', methods=['POST', 'GET'])
def activate_gold():
    return render_template('activate_gold.html', user=current_user)


def confirmation_required(desc_fn):
    def inner(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if request.args.get('confirm') != '1':
                desc = desc_fn()
                return redirect(url_for('confirm',
                                        desc=desc, action_url=quote(request.url)))
            return f(*args, **kwargs)

        return wrapper

    return inner


@login_required
@confirmation_required(you_sure)
@views.route(
    '/CancelA@IIi10OOo83889RPrnm9B187E0048830A48F0134D5E217F1CDCA208D8797DC0D36825E6BB6DD00OLJLjlijOD%OO81liLLl?!%$%OO8083E3E838380OOOO5432mnnmnIl1i1lIlLO8D0D0D')
def cancel():
    server_funcs.cancel_membership(username=flask_login.current_user.email)
    flash("Cancelled Paid Membership! Taking you to your free account details now.")
    return redirect(url_for('views.account_page'))
