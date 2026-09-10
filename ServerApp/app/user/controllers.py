from sqlalchemy.exc import IntegrityError
from app import *
from .models import User
import os
import sqlite3
import secrets
import time

from werkzeug.security import generate_password_hash, check_password_hash

mod_user = Blueprint('user', __name__)

NET_SEC_PASSWD = os.environ.get('SECURETEA_NET_SECRET', 'PASSWD')
NETWORK_SECRET = NET_SEC_PASSWD
net_sec = NET_SEC_PASSWD

DB_PATH = 'example.db'
SESSION_TTL = 12 * 60 * 60


def _get_conn():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con


def _init_db(con):
    cur = con.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS users(
        username text NOT NULL PRIMARY KEY,
        password text NOT NULL)''')
    cur.execute('''CREATE TABLE IF NOT EXISTS sessions(
        token text NOT NULL PRIMARY KEY,
        username text NOT NULL,
        created_at integer NOT NULL)''')
    con.commit()


def is_logged_in(token):
    """Check if the session token exists and has not expired."""
    if not token:
        return False
    con = _get_conn()
    try:
        cur = con.cursor()
        row = cur.execute(
            "SELECT created_at FROM sessions WHERE token=?",
            (token,)
        ).fetchone()
        if row is None:
            return False
        return (int(time.time()) - int(row["created_at"])) < SESSION_TTL
    finally:
        con.close()


@mod_user.route('/userlogin', methods=['POST'])
def login():
    """Endpoint to manage user login"""
    uname = request.json.get("username") if request.json else None
    passwd = request.json.get("password") if request.json else None
    ns = request.json.get("ns") if request.json else None

    if not uname or not passwd:
        return jsonify('username and password required'), 400
    if ns != net_sec:
        return jsonify('Network Secret is incorrect'), 403

    con = _get_conn()
    try:
        _init_db(con)
        cur = con.cursor()
        row = cur.execute(
            "SELECT password FROM users WHERE username=?",
            (uname,)
        ).fetchone()
        if row is None or not check_password_hash(row["password"], passwd):
            return jsonify('username password incorrect'), 401

        token = secrets.token_urlsafe(32)
        cur.execute(
            "DELETE FROM sessions WHERE username=?",
            (uname,)
        )
        cur.execute(
            "INSERT INTO sessions(token, username, created_at) VALUES (?, ?, ?)",
            (token, uname, int(time.time()))
        )
        con.commit()
        return jsonify({'cookie': token, 'username': uname})
    finally:
        con.close()


@mod_user.route('/userlogout', methods=['POST'])
def logout():
    """Endpoint to manage user logout"""
    token = None
    try:
        token = request.json.get("cookie")
    except Exception:
        pass
    if token:
        con = _get_conn()
        try:
            cur = con.cursor()
            cur.execute("DELETE FROM sessions WHERE token=?", (token,))
            con.commit()
        finally:
            con.close()
    return jsonify(success=True)


@mod_user.route('/register', methods=['POST'])
def create_user():
    """Endpoint to create a new user"""
    uname = request.json.get("username") if request.json else None
    passwd = request.json.get("password") if request.json else None
    ns = request.json.get("ns") if request.json else None

    if not uname or not passwd:
        return jsonify('username and password required'), 400
    if ns != net_sec:
        return jsonify('Network Secret is incorrect'), 403

    con = _get_conn()
    try:
        _init_db(con)
        cur = con.cursor()
        cur.execute(
            "INSERT INTO users(username, password) VALUES (?, ?)",
            (uname, generate_password_hash(passwd))
        )
        con.commit()
        return jsonify('Registration Sucessful'), 200
    except sqlite3.IntegrityError:
        return jsonify('Two users with same Username'), 400
    finally:
        con.close()
