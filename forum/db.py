from functools import wraps
from flask import session, redirect, url_for
import mysql.connector


# Skapar en anslutning till databasen "forum" i XAMPP.
def get_db():
    return mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="",          # XAMPP har tomt lösenord som standard
        database="forum"
    )


# Dekorator som kollar att man är inloggad. Annars skickas man till inloggningssidan.
def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("main.login"))
        return f(*args, **kwargs)
    return wrapper