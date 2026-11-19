from flask import Flask, render_template, request, redirect, session, url_for, abort
import mysql.connector

app = Flask(__name__)
app.secret_key = "byt-ut-mig-till-nagot-eget"


def get_db():
    return mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="",          # XAMPP har tomt lösenord som standard
        database="forum"
    )


@app.route("/", methods=["GET", "POST"])
def login():
    fel = None
    if request.method == "POST":
        db = get_db()
        cur = db.cursor(dictionary=True)
        cur.execute(
            "SELECT * FROM users WHERE username = %s AND password = %s",
            (request.form["username"], request.form["password"])
        )
        user = cur.fetchone()
        cur.close()
        db.close()
        if user:
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect(url_for("forum"))
        fel = "Fel användarnamn eller lösenord"
    return render_template("login.html", fel=fel)


@app.route("/forum", methods=["GET", "POST"])
def forum():
    if "user_id" not in session:
        return redirect(url_for("login"))

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


@app.route("/topic/<int:topic_id>")
def topic(topic_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

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


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)