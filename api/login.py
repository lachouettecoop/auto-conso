import os

import ldap
from flask import Blueprint, Response, abort, jsonify, request
from flask_jwt_extended import create_access_token

LDAP_SERVER = os.environ.get("LDAP_SERVER", "ldap://ldap.lachouettecoop.fr:389")
LDAP_BASE_DN = os.environ.get("LDAP_BASE_DN", "cn=admin,dc=lachouettecoop,dc=fr")
LDAP_SEARCH_DN = os.environ.get("LDAP_SEARCH_DN", "dc=lachouettecoop,dc=fr")
LDAP_USER_DN = os.environ.get(
    "LDAP_USER_DN", "cn={},ou=membres,o=lachouettecoop,dc=lachouettecoop,dc=fr"
)
LDAP_ADMIN_PASS = os.environ.get("LDAP_ADMIN_PASS")
LDAP_SCOPE_SUBTREE = 2

ONLY_USERS = os.environ.get("ONLY_USERS", "").split(",")
ONLY_USERS = [user.strip().lower() for user in ONLY_USERS]

blueprint = Blueprint("login", __name__)


def build_profile(user):
    try:
        ldap_connection = ldap.initialize(LDAP_SERVER)
        ldap_connection.simple_bind_s(LDAP_BASE_DN, LDAP_ADMIN_PASS)
        result = ldap_connection.search_s(LDAP_SEARCH_DN, LDAP_SCOPE_SUBTREE, "cn={}".format(user))
        ldap_connection.unbind_s()

        return {
            "user": user,
            "name": result[0][1]["sn"][0].decode("utf-8"),
            "lastname": result[0][1]["description"][0].decode("utf-8"),
        }
    except Exception as e:
        abort(Response(f"Authentication failed for {user}: {str(e)}", 403))


@blueprint.route("/api/login", methods=["POST"])
def login():
    # extract credentials from the request
    credentials = request.json
    email = credentials.get("email")
    password = credentials.get("password")
    if not credentials or not email or not password:
        abort(Response("Missing or bad credentials", 400))

    if ONLY_USERS and email.lower() not in ONLY_USERS:
        abort(Response("User not authorized", 400))

    # authenticate against some identity source, such as LDAP or a database
    try:
        ldap_connection = ldap.initialize(LDAP_SERVER)
        ldap_connection.simple_bind_s(LDAP_USER_DN.format(email), password)
        ldap_connection.unbind_s()
    except Exception as e:
        abort(Response(f"Authentication failed for {email}: {str(e)}", 403))
    token = create_access_token(identity=build_profile(email))
    return jsonify(token=token)
