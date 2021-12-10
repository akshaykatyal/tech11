# importing the required libraries for the google login application
import json
import os
import sqlite3
import sys

# using the flask as the API for the calls
from flask import Flask, render_template, redirect, request, url_for
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
# using the library for the authentication using Goggle social media web application
from oauthlib.oauth2 import WebApplicationClient
import requests

# getting the data and storing the data to db
from data_db import init_user_command
from user_info import Google_User

# getting the client-id and secret to authenticate to the google api
PYTHON_GOOGLE_CLIENT_ID = "730762102709-1i5h0d6e176guuhtfnlg7bip6rflgh4u.apps.googleusercontent.com"
PYTHON_GOOGLE_CLIENT_SECRET = "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"
PYTHON_GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"


# setting up the flask application
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)

# using the login manager to perform the google login
login_manager = LoginManager()
login_manager.init_app(app)

# linking the application to the database
try:
    init_user_command()
except sqlite3.OperationalError:
    # raising the exception error is sqlite database is not found
    pass

# linking to google for the login to the application
client = WebApplicationClient(PYTHON_GOOGLE_CLIENT_ID)

# Getting the user details if present in the database
@login_manager.user_loader
def load_user(user_id):
    # getting the user-id of the user
    return Google_User.user_get(user_id)


# routing the login page for the Hello API application using google login
@app.route("/")
def index():
    # checking the user is authenticated or not
    if current_user.is_authenticated:
        return render_template(
            "index.html",
            user_name=current_user.name,
            user_email=current_user.email,
            user_profile_pic=current_user.profile_pic,
        )
    else:
        return render_template("login.html")

# Getting google login configuration
def get_google_provider_cfg():
    return requests.get(PYTHON_GOOGLE_DISCOVERY_URL).json()


@app.route("/login")
def user_login():
    # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # getting the login details for the user and also retrieving the details ike picture, mail-id
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )

    return redirect(request_uri)


# Getting callback login
@app.route("/login/callback")
def callback():
    # verifying on the device for 2-step verification whether the code matches or not, this is then redirected
    verification_code= request.args.get("code")
    result = "<p>code: " + verification_code + "</p>"

    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    # getting the login token for the user login
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=verification_code,
    )
    # getting the login response if successful
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(PYTHON_GOOGLE_CLIENT_ID, PYTHON_GOOGLE_CLIENT_SECRET),
    )

    # parsing the json response and then displaying the result
    client.parse_request_body_response(json.dumps(token_response.json()))

    # getting the user complete details from google and displaying on successful login
    google_userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(google_userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    result = result + "<p>token_response: " + token_response.text + "</p>"

    # verifying the credentials and  getting the email, picture, and name
    if userinfo_response.json().get("email_verified"):
        google_unique_id = userinfo_response.json()["sub"]
        google_users_email = userinfo_response.json()["email"]
        google_picture = userinfo_response.json()["picture"]
        google_users_name = userinfo_response.json()["given_name"]
    else:
        return "User email not available or not verified by Google.", 400

    # storing the user details in the database
    user = Google_User(id_=google_unique_id, name=google_users_name, email=google_users_email, profile_pic=google_picture)

    # checking the user details in the database
    if not Google_User.user_get(google_unique_id):
        Google_User.create_user(google_unique_id, google_users_name, google_users_email, google_picture)

    # logging the user
    login_user(user)

    # displaying the page with details
    return redirect(url_for("index"))


# function to logout the google login from web-app
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))

# running the application at url 127.0.0.1:5000
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000,ssl_context="adhoc")
