from flask import (
    redirect,
    Blueprint,
    render_template,
    request,
    current_app,
    session
)
import requests
import json
import random
import string
from src.dependencies.users_api import UserApi

login = Blueprint("login", __name__)


@login.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        payload = {}
        payload["fullname"] = request.form['name']
        payload["email"] = request.form['email'].lower()
        payload["password"] = request.form['password']

        json_data = UserApi().register_user(payload)

        if json_data.get('message') == 'email taken':
            return render_template(
                "pages/register.html", error="email-taken"
            )

        else:
            UserApi().create_folder(json_data['id'])

            return redirect('./login')
    return render_template('pages/register.html')


@login.route("/reset_pass", methods=["GET", 'POST'])
def reset_pass():
    if request.method == 'GET':
        return render_template(
            "pages/reset_pass.html"
        )
    if request.method == 'POST':

        get_code = generate_random_string()

        url = current_app.config["EMAIL_API_URL"] + "/send_email"
        headers = {"Content-type": "application/json", "Accept": "text/plain"}
        email = request.form['email'].lower()
        payload = {}
        payload["email"] = email
        payload["company_name"] = "Extract Engine"
        payload["type"] = "reset_pass_email"
        payload['template'] = 'reset_pass'
        payload['title'] = 'Reset your password'
        payload['link'] = f'{current_app.config["LOGIN_URL"]}/new_pass/{email}/{get_code}'

        response = requests.request(
            "POST", url, data=json.dumps(payload), headers=headers
        )
        url = current_app.config["USER_API_URL"] + "/update"

        payload = {}
        payload["email"] = email
        payload["code"] = get_code

        headers = {"Content-type": "application/json", "Accept": "text/plain"}

        response = requests.request(
            "PUT", url, data=json.dumps(payload), headers=headers
        )

        json_data = json.loads(response.text)

        if response.status_code != 200:
            # code u001 has been specified to be an incorrect email and
            # password combination so we should check for this
            if json_data["error_code"] == "u001":
                return render_template(
                    "pages/new_pass.html",
                    error="reset-pass-not-sent"
                )

        return render_template(
            "pages/login.html", error="reset-pass-sent"
        )


@login.route('/login', methods=['GET', 'POST'])
def display_login_page():
    # session["next"] = request.args.get("next", "/")
    session['info-message'] = ''
    if request.method == 'POST':

        post_data = request.form

        payload = {}
        payload["email"] = post_data["email"].lower()
        payload["password"] = post_data["password"]
        json_data = UserApi().login(payload)
        # code u001 has been specified to be an incorrect email and
        # password combination so we should check for this
        if json_data.get("message") == "Invalid credentials":
            return render_template(
                "pages/login.html",
                error="error-password-username"
            )
        session['email'] = json_data['email']
        session['access_token'] = json_data['access_token']
        session['refresh_token'] = json_data['refresh_token']
        session['id'] = json_data['user_id']

        if "keep_me_logged_in" in post_data:
            if post_data["keep_me_logged_in"] == "true":
                session["keep_me_logged_in"] = "logged_in"
                session.permanent = True

        session["cookie_policy"] = "yes"
        session["error"] = ""
        return redirect('./extract')

    else:
        if session.get("keep_me_logged_in"):
            if session["keep_me_logged_in"] == "logged_in":
                if 'access_token' not in session:
                    return render_template(
                        "pages/login.html", error="jwt-not-in-session"
                    )
                return redirect('./extract')

    return render_template(
        "pages/login.html"
    )


@login.route("/logout")
def logout():
    session.clear()
    return redirect('./login')


@login.route("/new_pass/<email>/<random>", methods=["GET", "POST"])
def set_new_pass(email, random):
    get_email = email.lower()
    get_random = random
    if request.method == "GET":
        return render_template(
            "pages/new_pass.html",
            email=get_email,
            random=get_random
            )
    if request.method == "POST":
        if get_random == " ":
            return render_template(
                "pages/new_pass.html",
                error="invalid-code"
            )

        payload = {}
        payload["password"] = request.form["password"]
        payload["email"] = get_email.lower()
        payload["code"] = get_random

        json_data = UserApi().update_pass(payload)

        # code u001 has been specified to be an incorrect email and
        # password combination so we should check for this
        if json_data["message"] == "Invalid code" or json_data["message"] == "Code not sent":
            return render_template(
                "pages/new_pass.html",
                error="invalid-code"
            )
        elif json_data["message"] == "Code expired":
            return render_template(
                "pages/new_pass.html",
                error="expired"
            )

        return render_template("pages/login.html", error="new-pass-set")


def generate_random_string(length=8):
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choice(characters) for _ in range(length))
