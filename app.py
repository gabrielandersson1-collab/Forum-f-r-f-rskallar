from flask import Flask, render_template, request, redirect, session, url_for
import mysql.connector

app = Flask(__name__)
app.secret_key = "byt-ut-mig-till-nagot-eget"

def get_db():
    return mysql.connector.connect(
        host="localhost",
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
            return redirect(url_for("skriv"))
        fel = "Fel användarnamn eller lösenord"
    return render_template("login.html", fel=fel)

@app.route("/skriv", methods=["GET", "POST"])
def skriv():
    if "user_id" not in session:
        return redirect(url_for("login"))
    if request.method == "POST":
        db = get_db()
        cur = db.cursor()
        cur.execute(
            "INSERT INTO posts (user_id, content) VALUES (%s, %s)",
            (session["user_id"], request.form["content"])
        )
        db.commit()
        cur.close()
        db.close()
        return redirect(url_for("skriv"))
    return render_template("skriv.html", username=session["username"])

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)