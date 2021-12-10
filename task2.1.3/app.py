# importing all the required files
import logging
from flask import Flask, g, jsonify
from flask_oidc import OpenIDConnect
import json
import requests

# performing debug using Keycloak
logging.basicConfig(level=logging.DEBUG)

# running the flask application instance
app = Flask(__name__)
# configuring keycloak application for user login
app.config.update({
    'SECRET_KEY': 'ff6114aa-a3af-4531-8a71-a121bc40da42',
    'TESTING': True,
    'DEBUG': True,
    'OIDC_CLIENT_SECRETS': 'secrets.json',
    'OIDC_ID_TOKEN_COOKIE_SECURE': False,
    'OIDC_REQUIRE_VERIFIED_EMAIL': False,
    'OIDC_USER_INFO_ENABLED': True,
    'OIDC_OPENID_REALM': 'myRealm',
    'OIDC_SCOPES': ['openid', 'email', 'profile'],
    'OIDC_INTROSPECTION_AUTH_METHOD': 'client_secret_post'
})
# using the keycloak open-id connect
keycloak_oidc = OpenIDConnect(app)


@app.route('/')
# function to login to keycloak homepage
def keycloak_home():
    if keycloak_oidc.user_loggedin:
        return ('Good Day from Hello World Home Page, %s, <a href="/private">See private</a> '
                '<a href="/logout">Log out from Keycloak</a>') % \
               keycloak_oidc.user_getfield('preferred_username')
    else:
        return 'Good Day from Hello World Home Page, <a href="/private">Log in</a>'


@app.route('/private')
@keycloak_oidc.require_login
def hello_me():
    # getting the username, email for the login user
    info = keycloak_oidc.user_getinfo(['preferred_username', 'email', 'sub'])

    # getting the username, email, and id of the user
    username = info.get('preferred_username')
    email = info.get('email')
    user_id = info.get('sub')

    if user_id in keycloak_oidc.credentials_store:
        try:
            # using Oauth for the client login
            from oauth2client.client import OAuth2Credentials
            access_token = OAuth2Credentials.from_json(keycloak_oidc.credentials_store[user_id]).access_token
            # getting the access token for the keycloak
            print('access_token=<%s>' % access_token)

        except:
            print("Could not access greeting-service")


    return ("""Hello %s your email is %s and your user_id is %s!
               <ul>
                 <li><a href="/">Home</a></li>
                 <li><a href="//localhost:8080/auth?referrer=flask-app&referrer_uri=http://localhost:5000/private&">Account</a></li>
                </ul>""" %
            (username, email, user_id))


# getting the api for the application this displays the welcome message
@app.route('/api', methods=['POST'])
@keycloak_oidc.accept_token(require_token=True, scopes_required=['openid'])
def keycloak_hello_api():
    return json.dumps({'Hello John': 'Welcome John %s' % g.oidc_token_info['sub']})

# function to perform logout for web application
@app.route('/logout')
def logout():
    # calling the logout function
    keycloak_oidc.logout()
    return 'Hi John, you have been logged out! <a href="/">Return</a>'


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=int('5001'), debug=True)
