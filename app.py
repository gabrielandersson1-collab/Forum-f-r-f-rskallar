from functools import wraps
from flask import Flask, render_template, request, redirect, session, url_for, abort
from werkzeug.security import check_password_hash
import mysql.connector

app = Flask(__name__)
app.secret_key = "a8f92c7d4e..."


# Skapar en anslutning till databasen "forum" i XAMPP alla routes använder den här
def get_db():
    return mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="",          # XAMPP har tomt lösenord som standard
        database="forum"
    )


# Dekorator som kollar att man är inloggada annars skickas man till inloggningssidan.
def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrapper


# visar inloggningsformuläret och kollar användarnamn och lösenord mot databasen
@app.route("/", methods=["GET", "POST"])
def login():
    fel = None
    if request.method == "POST":
        db = get_db()
        cur = db.cursor(dictionary=True)
        cur.execute(
            "SELECT * FROM users WHERE username = %s",
            (request.form["username"],)
        )
        user = cur.fetchone()
        cur.close()
        db.close()
        if user and check_password_hash(user["password"], request.form["password"]):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect(url_for("forum"))
        fel = "Fel användarnamn eller lösenord"
    return render_template("login.html", fel=fel)


# Loggar ut genom att tömma sessionen och skickar tillbaka till inloggningen
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# visar alla trådar GET och sparar en ny tråd i databasen när man skickar formuläret POST
@app.route("/forum", methods=["GET", "POST"])
@login_required
def forum():
    db = get_db()
    cur = db.cursor(dictionary=True)

    if request.method == "POST":
        cur.execute(
            "INSERT INTO topics (title, user_id) VALUES (%s, %s)",
            (request.form["title"], session["user_id"])
        )
        db.commit()
        new_id = cur.lastrowid
        cur.close()
        db.close()
        return redirect(url_for("topic", topic_id=new_id))

    cur.execute("""
        SELECT topics.id, topics.title, topics.created_at, users.username
        FROM topics
        JOIN users ON topics.user_id = users.id
        ORDER BY topics.created_at DESC
    """)
    topics = cur.fetchall()
    cur.close()
    db.close()
    return render_template("forum.html", username=session["username"], topics=topics)


# Visar en tråd med alla inlägg GET och sparar ett nytt svar POST .
@app.route("/topic/<int:topic_id>", methods=["GET", "POST"])
@login_required
def topic(topic_id):
    db = get_db()
    cur = db.cursor(dictionary=True)

    cur.execute("""
        SELECT topics.id, topics.title, users.username
        FROM topics
        JOIN users ON topics.user_id = users.id
        WHERE topics.id = %s
    """, (topic_id,))
    t = cur.fetchone()
    if not t:
        cur.close()
        db.close()
        abort(404)

    if request.method == "POST":
        cur.execute(
            "INSERT INTO posts (user_id, topic_id, content) VALUES (%s, %s, %s)",
            (session["user_id"], topic_id, request.form["content"])
        )
        db.commit()
        cur.close()
        db.close()
        return redirect(url_for("topic", topic_id=topic_id))   # post-redirect-get

    cur.execute("""
        SELECT posts.content, posts.created_at, users.username
        FROM posts
        JOIN users ON posts.user_id = users.id
        WHERE posts.topic_id = %s
        ORDER BY posts.created_at ASC
    """, (topic_id,))
    posts = cur.fetchall()
    cur.close()
    db.close()
    return render_template("topic.html", username=session["username"], topic=t, posts=posts)


if __name__ == "__main__":
    app.run(debug=True)