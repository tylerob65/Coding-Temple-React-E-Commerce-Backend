from flask import request
from .models import Users
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from werkzeug.security import generate_password_hash, check_password_hash

basic_auth = HTTPBasicAuth(scheme='Bearer')
token_auth = HTTPTokenAuth()

@basic_auth.verify_password
def verify_password(username,password):
    user = Users.query.filter_by(username=username).first()
    print("got here")
    print(user)
    print(check_password_hash(user.password,password))
    if user and check_password_hash(user.password,password):
        return user


@token_auth.verify_token
def verify_token(token):
    print(token)
    user = Users.query.filter_by(apitoken=token).first()
    if user:
        return user